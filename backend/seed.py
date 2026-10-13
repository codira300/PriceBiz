import asyncio
from datetime import datetime

from app.database import database


SEED_DATA = [
    {
        "id": "seed_v1_001",
        "Product": "Cream",
        "Brand": "Nivea Radiant & Beauty",
        "Size": "400ml",
        "Price": "₦6,000",
        "Location": "Ikorodu, Lagos",
        "Source": "User",
        "Date": "2026-09-15",
    },
    {
        "id": "seed_v1_002",
        "Product": "Egg",
        "Brand": "Egg",
        "Size": "1",
        "Price": "₦200",
        "Location": "Ikorodu, Lagos",
        "Source": "Mini Farm",
        "Date": "2026-09-21",
    },
    {
        "id": "seed_v1_003",
        "Product": "Noodles",
        "Brand": "Chikki Chicken Flavour",
        "Size": "1",
        "Price": "₦300",
        "Location": "Ikorodu, Lagos",
        "Source": "Shop",
        "Date": "2026-09-21",
    },
]


def parse_price(price: str) -> int:
    amount = price.replace("₦", "").replace(",", "").strip()
    return int(float(amount) * 100)


def parse_location(location: str) -> dict:
    lga, state = [part.strip() for part in location.split(",", 1)]
    
    return {
        "country": "Nigeria",
        "state": state,
        "lga": lga,
    }


async def get_or_create_source(source_name: str):
    source_type = "COMMUNITY" if source_name == "User" else "RETAILER"

    source = await database.sources.find_one({"name": source_name})

    if source:
        return source

    source = {
        "type": source_type,
        "name": source_name,
        "verification_status": "VERIFIED",
    }

    result = await database.sources.insert_one(source)

    return await database.sources.find_one({"_id": result.inserted_id})


async def get_or_create_location(location_data: dict):
    location = await database.locations.find_one(location_data)

    if location:
        return location

    result = await database.locations.insert_one(location_data)

    return await database.locations.find_one({"_id": result.inserted_id})


async def get_or_create_product(row: dict):
    product = await database.products.find_one({"name": row["Brand"]})

    if product:
        return product

    product = {
        "name": row["Brand"],
        "brand": row["Brand"],
        "status": "ACTIVE",
    }

    result = await database.products.insert_one(product)

    return await database.products.find_one({"_id": result.inserted_id})


async def get_or_create_variant(product: dict, row: dict):
    variant = await database.product_variants.find_one({
        "product_id": str(product["_id"]),
        "name": row["Size"],
    })

    if variant:
        return variant

    variant = {
        "product_id": str(product["_id"]),
        "name": row["Size"],
        "attributes": {
            "size": row["Size"]
        },
        "status": "ACTIVE",
    }

    result = await database.product_variants.insert_one(variant)

    return await database.product_variants.find_one({"_id": result.inserted_id})


async def create_observation(row, product, variant, location, source):
    observed_at = datetime.fromisoformat(row["Date"])

    existing = await database.price_observations.find_one({
        "product_id": str(product["_id"]),
        "variant_id": str(variant["_id"]),
        "price.amount": parse_price(row["Price"]),
        "location_id": str(location["_id"]),
        "source_id": str(source["_id"]),
        "observed_at": observed_at,
    })

    if existing:
        return existing

    observation = {
        "product_id": str(product["_id"]),
        "variant_id": str(variant["_id"]),
        "price": {
            "amount": parse_price(row["Price"]),
            "currency": "NGN",
        },
        "location_id": str(location["_id"]),
        "source_id": str(source["_id"]),
        "evidence": {
            "type": "USER_SUBMISSION",
            "image_url": None,
            "url": None,
            "note": None,
        },
        "feedback": {
            "useful": 0,
            "not_useful": 0,
            "reports": 0,
        },
        "observed_at": observed_at,
        "status": "ACTIVE",
    }

    result = await database.price_observations.insert_one(observation)

    return await database.price_observations.find_one({"_id": result.inserted_id})


async def seed_database():
    print("Starting seed...")

    for row in SEED_DATA:
        raw_observation = await database.raw_observations.find_one({
        "source.name": "seed_data_v1",
        "external_id": row["id"]
        })

        if raw_observation:
            print(f"Already processed: {row['Brand']} - {row['Price']}")
            continue

        source = await get_or_create_source(row["Source"])

        location_data = parse_location(row["Location"])
        location = await get_or_create_location(location_data)

        product = await get_or_create_product(row)

        variant = await get_or_create_variant(product, row)

        observation = await create_observation(
            row,
            product,
            variant,
            location,
            source,
        )

        raw_document = {
            "source": {
                "type": "ADMIN",
                "name": "seed_data_v1",
            },
            "external_id": row["id"],
            "input_format": "SPREADSHEET",
            "payload": {
                key: value
                for key, value in row.items()
                if key != "id"
            },
            "processing": {
                "status": "PROCESSED",
                "observation_id": str(observation["_id"]),
                "processed_at": datetime.datetime.now(datetime.UTC)
            },
            "created_at": datetime.datetime.now(datetime.UTC),
        }

        await database.raw_observations.insert_one(raw_document)

        print(f"Processed: {row['Brand']} - {row['Price']}")

    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed_database())