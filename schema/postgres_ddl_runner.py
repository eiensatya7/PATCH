#!/usr/bin/env python3
"""
PostgreSQL DDL Script Runner

This script reads all PostgreSQL DDL scripts from the current directory
and executes them against a specified PostgreSQL database.
"""

import os
import glob
import sys
import logging
from pathlib import Path
from typing import List, Optional
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class PostgresDDLRunner:
    def __init__(self, host: str = "localhost", port: int = 5432,
                 database: str = "postgres", user: str = "postgres",
                 password: str = "", ssl_mode: str = "prefer"):
        """
        Initialize the PostgreSQL DDL Runner.

        Args:
            host: PostgreSQL server host
            port: PostgreSQL server port
            database: Database name
            user: Username
            password: Password
            ssl_mode: SSL mode (disable, allow, prefer, require)
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
            'sslmode': ssl_mode
        }
        self.connection = None
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establish connection to PostgreSQL database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.logger.info(f"Connected to PostgreSQL database: {self.connection_params['database']}")
            return True
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False

    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from PostgreSQL database")

    def find_ddl_scripts(self, directory: str = ".") -> List[str]:
        """
        Find all DDL script files in the specified directory.

        Args:
            directory: Directory to search for scripts (default: current directory)

        Returns:
            List of DDL script file paths, sorted alphabetically
        """
        # Look for common SQL file extensions
        patterns = ["*.sql", "*.ddl", "*.pgsql"]
        script_files = []

        for pattern in patterns:
            script_files.extend(glob.glob(os.path.join(directory, pattern)))

        # Remove duplicates and sort
        script_files = sorted(list(set(script_files)))

        self.logger.info(f"Found {len(script_files)} DDL script(s): {script_files}")
        return script_files

    def read_script_file(self, file_path: str) -> Optional[str]:
        """
        Read the contents of a DDL script file.

        Args:
            file_path: Path to the script file

        Returns:
            Script contents as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:
                    self.logger.info(f"Read script file: {file_path} ({len(content)} characters)")
                    return content
                else:
                    self.logger.warning(f"Script file is empty: {file_path}")
                    return None
        except IOError as e:
            self.logger.error(f"Failed to read script file {file_path}: {e}")
            return None

    def execute_script(self, script_content: str, file_name: str) -> bool:
        """
        Execute a DDL script against the database.

        Args:
            script_content: SQL script content
            file_name: Name of the script file (for logging)

        Returns:
            bool: True if execution successful, False otherwise
        """
        if not self.connection:
            self.logger.error("No database connection available")
            return False

        try:
            cursor = self.connection.cursor()

            # Split script into individual statements
            # This handles scripts with multiple SQL statements
            statements = [stmt.strip() for stmt in script_content.split(';') if stmt.strip()]

            self.logger.info(f"Executing {len(statements)} statement(s) from {file_name}")

            for i, statement in enumerate(statements, 1):
                try:
                    cursor.execute(statement)
                    self.logger.debug(f"Statement {i}/{len(statements)} executed successfully")
                except psycopg2.Error as e:
                    self.logger.error(f"Error executing statement {i} in {file_name}: {e}")
                    cursor.close()
                    return False

            cursor.close()
            self.logger.info(f"Successfully executed all statements from {file_name}")
            return True

        except psycopg2.Error as e:
            self.logger.error(f"Database error while executing {file_name}: {e}")
            return False

    def run_all_scripts(self, directory: str = ".") -> bool:
        """
        Find and execute all DDL scripts in the specified directory.

        Args:
            directory: Directory containing DDL scripts

        Returns:
            bool: True if all scripts executed successfully, False otherwise
        """
        if not self.connect():
            return False

        try:
            script_files = self.find_ddl_scripts(directory)

            if not script_files:
                self.logger.warning("No DDL script files found in the current directory")
                return True

            success_count = 0
            total_count = len(script_files)

            for script_file in script_files:
                self.logger.info(f"Processing script: {script_file}")

                script_content = self.read_script_file(script_file)
                if script_content is None:
                    continue

                if self.execute_script(script_content, os.path.basename(script_file)):
                    success_count += 1
                else:
                    self.logger.error(f"Failed to execute script: {script_file}")

            self.logger.info(f"Execution summary: {success_count}/{total_count} scripts executed successfully")
            return success_count == total_count

        finally:
            self.disconnect()


def main():
    """Main function to run the DDL script executor."""
    # import argparse
    #
    # parser = argparse.ArgumentParser(description="Execute PostgreSQL DDL scripts from current directory")
    # parser.add_argument("--host", default="localhost", help="PostgreSQL host (default: localhost)")
    # parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port (default: 5432)")
    # parser.add_argument("--database", "-d", required=True, help="Database name")
    # parser.add_argument("--user", "-u", default="postgres", help="Username (default: postgres)")
    # parser.add_argument("--password", "-p", default="", help="Password")
    # parser.add_argument("--ssl-mode", default="prefer",
    #                     choices=["disable", "allow", "prefer", "require"],
    #                     help="SSL mode (default: prefer)")
    # parser.add_argument("--directory", default=".", help="Directory containing DDL scripts (default: current)")
    # parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    #
    # args = parser.parse_args()
    #
    # if args.verbose:
    #
    #
    # # Prompt for password if not provided
    # if not args.password:
    #     import getpass
    #     args.password = getpass.getpass("PostgreSQL password: ")


    logging.getLogger().setLevel(logging.DEBUG)
    # Create and run the DDL runner

    runner = PostgresDDLRunner(
        host="localhost",
        port="5432",
        database="patch_db",
        user="patch_user",
        password="patch123",
        ssl_mode="allow"
    )

    success = runner.run_all_scripts(".")

    if success:
        print("All DDL scripts executed successfully!")
        sys.exit(0)
    else:
        print("Some DDL scripts failed to execute. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()