#!/usr/bin/env python3
"""
MySQL Connection Troubleshooting Script for YouthSpace
Tests various connection methods and provides diagnostics
"""

import os
import socket
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dns_resolution():
    """Test DNS resolution for MySQL hostname"""
    try:
        hostname = "mysql.hostinger.com"
        print(f"🔍 Testing DNS resolution for {hostname}...")
        
        # Try to resolve hostname
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip_address}")
        return ip_address
        
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print("💡 Possible solutions:")
        print("   - Check your internet connection")
        print("   - Try using a different DNS server (8.8.8.8, 1.1.1.1)")
        print("   - Check if your firewall is blocking DNS queries")
        return None

def test_port_connectivity(hostname, port=3306):
    """Test if MySQL port is accessible"""
    try:
        print(f"🔌 Testing port connectivity to {hostname}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is accessible on {hostname}")
            return True
        else:
            print(f"❌ Port {port} is not accessible on {hostname}")
            return False
            
    except Exception as e:
        print(f"❌ Port connectivity test failed: {e}")
        return False

def test_pymysql_connection():
    """Test PyMySQL connection with detailed error handling"""
    try:
        import pymysql
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in .env file")
            return False
            
        print(f"🔗 Testing PyMySQL connection...")
        print(f"📋 Connection string: {database_url}")
        
        # Parse connection details
        if database_url.startswith('mysql+pymysql://'):
            url_parts = database_url.replace('mysql+pymysql://', '').split('/')
            auth_host = url_parts[0]
            database = url_parts[1] if len(url_parts) > 1 else ''
            
            if '@' in auth_host:
                auth, host = auth_host.split('@')
                if ':' in auth:
                    user, password = auth.split(':', 1)
                else:
                    user, password = auth, ''
            else:
                print("❌ Invalid DATABASE_URL format")
                return False
                
            print(f"📊 Connection details:")
            print(f"   Host: {host}")
            print(f"   User: {user}")
            print(f"   Database: {database}")
            
            # Test connection with different timeout settings
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"✅ MySQL connection successful!")
                print(f"📊 MySQL version: {version[0]}")
                
                # Test database access
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"📋 Existing tables: {len(tables)} found")
                
            connection.close()
            return True
            
    except ImportError:
        print("❌ PyMySQL not installed")
        print("💡 Install with: pip install PyMySQL")
        return False
    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL operational error: {e}")
        print("💡 Possible solutions:")
        print("   - Check your credentials in .env file")
        print("   - Verify database name is correct")
        print("   - Check if your IP is whitelisted on Hostinger")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_alternative_mysql_connector():
    """Test with mysql-connector-python as alternative"""
    try:
        import mysql.connector
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return False
            
        print(f"🔗 Testing mysql-connector-python...")
        
        # Parse connection details
        if database_url.startswith('mysql+pymysql://'):
            url_parts = database_url.replace('mysql+pymysql://', '').split('/')
            auth_host = url_parts[0]
            database = url_parts[1] if len(url_parts) > 1 else ''
            
            if '@' in auth_host:
                auth, host = auth_host.split('@')
                if ':' in auth:
                    user, password = auth.split(':', 1)
                else:
                    user, password = auth, ''
            else:
                return False
                
            # Test connection
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                connection_timeout=30
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ mysql-connector-python connection successful!")
            print(f"📊 MySQL version: {version[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except ImportError:
        print("❌ mysql-connector-python not available")
        return False
    except Exception as e:
        print(f"❌ mysql-connector-python failed: {e}")
        return False

def main():
    """Run comprehensive connection tests"""
    print("🔧 MySQL Connection Diagnostics")
    print("=" * 50)
    
    # Test 1: DNS Resolution
    print("\n1️⃣ DNS Resolution Test")
    ip_address = test_dns_resolution()
    
    # Test 2: Port Connectivity
    print("\n2️⃣ Port Connectivity Test")
    if ip_address:
        test_port_connectivity(ip_address)
    else:
        test_port_connectivity("mysql.hostinger.com")
    
    # Test 3: PyMySQL Connection
    print("\n3️⃣ PyMySQL Connection Test")
    pymysql_success = test_pymysql_connection()
    
    # Test 4: Alternative Connector
    print("\n4️⃣ Alternative Connector Test")
    alt_success = test_alternative_mysql_connector()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if pymysql_success or alt_success:
        print("✅ MySQL connection is working!")
        print("🚀 You can proceed with the migration")
    else:
        print("❌ MySQL connection issues detected")
        print("\n💡 TROUBLESHOOTING STEPS:")
        print("1. Check your internet connection")
        print("2. Verify credentials in .env file")
        print("3. Contact Hostinger support to:")
        print("   - Verify your database is active")
        print("   - Check if your IP needs to be whitelisted")
        print("   - Confirm the correct hostname")
        print("4. Try connecting from a different network")
        print("5. Check Hostinger control panel for database status")

if __name__ == '__main__':
    main()
