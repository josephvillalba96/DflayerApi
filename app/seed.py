"""
Simple seed script para poblar la base de datos con:
- Un usuario administrador base inicial
- Catálogos mínimos relacionados con creación de contenido (planes de membresía, etc.)

Uso:
    DATABASE_URL debe estar configurada (.env o variable de entorno).

    python -m app.seed

En Docker (contenedor api):
    docker-compose exec api python -m app.seed
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from app.db.base import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserType, VerificationStatus, AccountStatus
from app.models.multiplier_plan import MembershipPlan
from app.models.audio_track import AudioTrack


def get_db() -> Session:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurada. No se puede ejecutar el seed.")
    return SessionLocal()


def seed_base_user(db: Session) -> None:
    """
    Crea un usuario administrador base si no existe.
    """
    admin_email = "admin@multiplux.com"
    admin_username = "admin"

    existing = (
        db.query(User)
        .filter((User.email == admin_email) | (User.username == admin_username))
        .first()
    )
    if existing:
        print(f"[seed] Usuario admin base ya existe: id={existing.user_id}")
        return

    password_hash = get_password_hash("Admin1234!")  # Cambiar inmediatamente en producción

    admin = User(
        username=admin_username,
        email=admin_email,
        password=password_hash,
        name="Administrador Base",
        user_type=UserType.ADMIN,
        is_business_account=False,
        verification_status=VerificationStatus.VERIFIED,
        account_status=AccountStatus.ACTIVE,
        email_verified=True,
        is_active=True,
        created_at=datetime.utcnow(),
        registration_date=datetime.utcnow(),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    print(f"[seed] Usuario admin creado: id={admin.user_id}, email={admin.email}")


def seed_membership_plans(db: Session) -> None:
    """
    Crea algunos planes de membresía (catálogo) si no existen.
    Estos planes se usan para monetización y pueden asociarse a usuarios.
    """
    plans_to_create = [
        {
            "plan_name": "Free",
            "price": 0.0,
            "multiplier": 1.0,
            "duration_days": 3650,  # 10 años simbólicos
            "description": "Plan básico gratuito con funcionalidades estándar.",
        },
        {
            "plan_name": "Pro",
            "price": 9.99,
            "multiplier": 2.0,
            "duration_days": 30,
            "description": "Plan Pro con mejores condiciones de monetización.",
        },
        {
            "plan_name": "Elite",
            "price": 29.99,
            "multiplier": 3.0,
            "duration_days": 30,
            "description": "Plan Elite con máxima multiplicación de ganancias.",
        },
    ]

    for data in plans_to_create:
        exists = (
            db.query(MembershipPlan)
            .filter(MembershipPlan.plan_name == data["plan_name"])
            .first()
        )
        if exists:
            print(f"[seed] Plan ya existe: {data['plan_name']}")
            continue

        plan = MembershipPlan(
            plan_name=data["plan_name"],
            price=data["price"],
            multiplier=data["multiplier"],
            duration_days=data["duration_days"],
            description=data["description"],
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        print(f"[seed] Plan creado: {plan.plan_name} (id={plan.plan_id})")


def seed_audio_tracks(db: Session) -> None:
    """
    Crea pistas de audio base que se pueden reutilizar como catálogo
    para contenidos (por ejemplo, música de fondo).
    No se asocian a un post específico todavía.
    """
    tracks_to_create = [
        {
            "title": "Lofi Chill Beat",
            "artist": "Multiplux Catalog",
            "storage_path": "audio/catalog/lofi_chill_beat.mp3",
            "format": "mp3",
            "duration_seconds": 180.0,
        },
        {
            "title": "Uplifting Corporate",
            "artist": "Multiplux Catalog",
            "storage_path": "audio/catalog/uplifting_corporate.mp3",
            "format": "mp3",
            "duration_seconds": 150.0,
        },
        {
            "title": "Podcast Intro",
            "artist": "Multiplux Catalog",
            "storage_path": "audio/catalog/podcast_intro.wav",
            "format": "wav",
            "duration_seconds": 30.0,
        },
    ]

    try:
        for data in tracks_to_create:
            exists = (
                db.query(AudioTrack)
                .filter(
                    AudioTrack.title == data["title"],
                    AudioTrack.artist == data["artist"],
                )
                .first()
            )
            if exists:
                print(f"[seed] AudioTrack ya existe: {data['title']} - {data['artist']}")
                continue

            track = AudioTrack(
                title=data["title"],
                artist=data["artist"],
                storage_path=data["storage_path"],
                format=data["format"],
                duration_seconds=data.get("duration_seconds"),
                is_original_audio=True,
                created_at=datetime.utcnow(),
            )
            db.add(track)
            db.commit()
            db.refresh(track)
            print(f"[seed] AudioTrack creado: {track.title} (id={track.audio_id})")
    except ProgrammingError as e:
        # Si la tabla audio_tracks no existe todavía, omitimos este seed
        if "audio_tracks" in str(e):
            print("[seed] Tabla 'audio_tracks' no existe todavía. Omitiendo seed de pistas de audio.")
            db.rollback()
        else:
            raise


def run_seed() -> None:
    db = get_db()
    try:
        print("[seed] Iniciando seed de base de datos...")
        seed_base_user(db)
        seed_membership_plans(db)
        seed_audio_tracks(db)
        print("[seed] Seed completado correctamente.")
    finally:
        db.close()


if __name__ == "__main__" or __package__ == "app.seed":
    run_seed()


