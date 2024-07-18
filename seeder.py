from app import app, db
from models import Item
from faker import Faker

fake = Faker()


def seeder():
    with app.app_context():
        items = []
        for _ in range(10):
            item = Item(name=fake.name())
            items.append(item)

        db.session.bulk_save_objects(items)
        db.session.commit()

        print("Seeding completed")


if __name__ == "__main__":
    seeder()
