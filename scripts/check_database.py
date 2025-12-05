#!/usr/bin/env python3
"""
Quick script to check what data is in your database
"""

from config import execute_query
from datetime import datetime

def check_database():
    print("=" * 80)
    print("DATABASE CONTENTS CHECK")
    print("=" * 80)
    print()

    try:
        # Check Airlines
        print("📋 AIRLINES:")
        print("-" * 80)
        airlines = execute_query("SELECT * FROM airline LIMIT 10")
        if airlines:
            for airline in airlines:
                print(f"  - {airline['airline_name']}")
        else:
            print("  ⚠️  No airlines found in database")
        print()

        # Check Airports
        print("✈️  AIRPORTS:")
        print("-" * 80)
        airports = execute_query("SELECT * FROM airport LIMIT 10")
        if airports:
            for airport in airports:
                print(f"  - {airport['airport_name']} ({airport['airport_city']})")
        else:
            print("  ⚠️  No airports found in database")
        print()

        # Check Airplanes
        print("🛩️  AIRPLANES:")
        print("-" * 80)
        airplanes = execute_query("SELECT * FROM airplane LIMIT 10")
        if airplanes:
            for plane in airplanes:
                print(f"  - {plane['airline_name']} - {plane['airplane_id']} ({plane['seats']} seats)")
        else:
            print("  ⚠️  No airplanes found in database")
        print()

        # Check Flights
        print("🛫 FLIGHTS:")
        print("-" * 80)
        flights = execute_query("""
            SELECT f.*,
                   a1.airport_city as departure_city,
                   a2.airport_city as arrival_city
            FROM flight f
            JOIN airport a1 ON f.departure_airport = a1.airport_name
            JOIN airport a2 ON f.arrival_airport = a2.airport_name
            ORDER BY f.departure_time DESC
            LIMIT 10
        """)

        if flights:
            print(f"  Found {len(flights)} flights (showing first 10):\n")
            for i, flight in enumerate(flights, 1):
                print(f"  {i}. {flight['airline_name']} Flight {flight['flight_num']}")
                print(f"     From: {flight['departure_airport']} ({flight['departure_city']})")
                print(f"     To:   {flight['arrival_airport']} ({flight['arrival_city']})")
                print(f"     Departs: {flight['departure_time']}")
                print(f"     Arrives: {flight['arrival_time']}")
                print(f"     Price: ${flight['price']}")
                print(f"     Status: {flight['status']}")
                print()
        else:
            print("  ⚠️  No flights found in database")
        print()

        # Check upcoming flights specifically
        print("📅 UPCOMING FLIGHTS (Status='Upcoming' and future dates):")
        print("-" * 80)
        upcoming = execute_query("""
            SELECT COUNT(*) as count
            FROM flight
            WHERE status = 'Upcoming' AND departure_time > NOW()
        """, fetch_one=True)

        print(f"  Total upcoming flights: {upcoming['count']}")
        print()

        # Check Customers
        print("👥 CUSTOMERS:")
        print("-" * 80)
        customers = execute_query("SELECT COUNT(*) as count FROM customer", fetch_one=True)
        print(f"  Total customers: {customers['count']}")
        print()

        # Check Booking Agents
        print("💼 BOOKING AGENTS:")
        print("-" * 80)
        agents = execute_query("SELECT COUNT(*) as count FROM booking_agent", fetch_one=True)
        print(f"  Total booking agents: {agents['count']}")
        print()

        # Check Airline Staff
        print("👔 AIRLINE STAFF:")
        print("-" * 80)
        staff = execute_query("SELECT COUNT(*) as count FROM airline_staff", fetch_one=True)
        print(f"  Total staff members: {staff['count']}")
        print()

        # Check Tickets
        print("🎫 TICKETS:")
        print("-" * 80)
        tickets = execute_query("SELECT COUNT(*) as count FROM ticket", fetch_one=True)
        print(f"  Total tickets issued: {tickets['count']}")
        print()

        print("=" * 80)
        print("✅ Database check complete!")
        print()

        # Recommendations
        if not airlines or len(airlines) == 0:
            print("⚠️  WARNING: No airlines in database. You need to add airlines first.")
        if not airports or len(airports) == 0:
            print("⚠️  WARNING: No airports in database. You need to add airports first.")
        if not flights or len(flights) == 0:
            print("⚠️  WARNING: No flights in database. You need to add flights first.")
            print()
            print("To add sample data, you can:")
            print("1. Log in as airline staff (with Admin permission)")
            print("2. Add airports via the 'Add Airport' menu")
            print("3. Add airplanes via the 'Add Airplane' menu")
            print("4. Add flights via the 'Add Flight' menu")

        print("=" * 80)

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print()
        print("Make sure:")
        print("1. MySQL/MariaDB is running (XAMPP started)")
        print("2. Database 'airline_portal' exists")
        print("3. All tables are created")
        print("4. Database credentials in config.py are correct")

if __name__ == '__main__':
    check_database()
