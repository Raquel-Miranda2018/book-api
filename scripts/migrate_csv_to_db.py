def print_summary():
    """Print database summary"""
    from sqlalchemy import func

    db = SessionLocal()
    try:
        total_books = db.query(func.count(Book.id)).scalar() or 0
        total_categories = db.query(func.count(func.distinct(Book.category))).scalar() or 0

        avg_price = db.query(func.avg(Book.price)).scalar()
        min_price = db.query(func.min(Book.price)).scalar()
        max_price = db.query(func.max(Book.price)).scalar()

        print("\n" + "=" * 50)
        print("📊 DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total Books: {total_books}")
        print(f"Total Categories: {total_categories}")

        if avg_price is not None:
            print(f"Average Price: £{avg_price:.2f}")
            print(f"Min Price: £{min_price:.2f}")
            print(f"Max Price: £{max_price:.2f}")

        print(f"Database: {engine.url}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    finally:
        db.close()