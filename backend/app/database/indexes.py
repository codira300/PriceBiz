from app.database.connection import database


async def initialize_indexes():
    await database.users.create_index(
        "email",
        unique=True,
        sparse=True,
    )

    await database.users.create_index(
        "phone",
        unique=True,
        sparse=True,
    )

    await database.users.create_index(
        "auth.google_id",
        unique=True,
        sparse=True,
    )

    
    await database.product_variants.create_index(
        "product_id"
    )


    await database.price_observations.create_index(
        [
            ("product_id", 1),
            ("variant_id", 1),
        ]
    )

    await database.price_observations.create_index(
        [
            ("location_id", 1),
            ("observed_at", -1),
        ]
    )

    await database.price_observations.create_index(
        [
            ("product_id", 1),
            ("observed_at", -1),
        ]
    )
    
    await database.price_observations.create_index(
            "raw_observation_id",
            unique=True,
            sparse=True,
    )

    
    await database.locations.create_index(
        [
            ("country", 1),
            ("state", 1),
            ("lga", 1),
            ("area", 1),
            ("market", 1),
        ]
    )

    
    await database.sources.create_index(
        "type"
    )

    
    await database.raw_observations.create_index(
        "input_format"
    )

    await database.raw_observations.create_index(
        "processing_status"
    )

    # Posts
    await database.posts.create_index(
        [
            ("created_at", -1),
        ]
    )

    await database.posts.create_index(
        [
            ("author_id", 1),
            ("created_at", -1),
        ]
    )

    await database.posts.create_index(
        [
            ("product_id", 1),
            ("created_at", -1),
        ]
    )

    await database.posts.create_index(
        [
            ("location_id", 1),
            ("created_at", -1),
        ]
    )


    await database.comments.create_index(
        [
            ("post_id", 1),
            ("created_at", 1),
        ]
    )

    await database.comments.create_index(
        [
            ("post_id", 1),
            ("parent_comment_id", 1),
            ("created_at", 1),
        ]
    )

    await database.comments.create_index(
        [
            ("author_id", 1),
            ("created_at", -1),
        ]
    )

    await database.reactions.create_index(
        [
            ("user_id", 1),
            ("target_type", 1),
            ("target_id", 1),
        ],
        unique=True,
    )

    await database.reactions.create_index(
        [
            ("target_type", 1),
            ("target_id", 1),
        ]
    )
    
    await database.refresh_tokens.create_index(
        "token_hash",
        unique=True,
    )

    await database.refresh_tokens.create_index(
        "user_id"
    )

    await database.refresh_tokens.create_index(
        "family_id"
    )

    await database.refresh_tokens.create_index(
        "expires_at"
    )
    
    