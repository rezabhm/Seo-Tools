def input_with_default(prompt, default):
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default


print("Choose environment mode:")
print("1) Development (dev)")
print("2) Production (deployment)")
env_choice = input("Enter choice (1 or 2) [default: 1]: ").strip()

ENVIRONMENT = "production" if env_choice == "2" else "dev"
print(f"Selected environment: {ENVIRONMENT}")

# Common inputs
DJANGO_PORT = input_with_default("Django Port", "8000")

# Development settings
DEV_DB_NAME = input_with_default("DEV Database Name", "ClickReservationSystem")
DEV_DB_USER = input_with_default("DEV Database User", "postgres")
DEV_DB_PASSWORD = input_with_default("DEV Database Password", "user@1234")
DEV_DB_HOST = input_with_default("DEV Database Host", "host.docker.internal")
DEV_DB_PORT = input_with_default("DEV Database Port", "5432")
DEV_CORS_ALLOWED_ORIGINS = input_with_default("DEV CORS Allowed Origins (comma separated)", "http://localhost:3000")

# Production settings
PROD_DB_NAME = input_with_default("PRODUCTION Database Name", "ClickReservationSystem")
PROD_DB_USER = input_with_default("PRODUCTION Database User", "postgres")
PROD_DB_PASSWORD = input_with_default("PRODUCTION Database Password", "user@1234")
PROD_DB_HOST = input_with_default("PRODUCTION Database Host", "host.docker.internal")
PROD_DB_PORT = input_with_default("PRODUCTION Database Port", "5432")
PROD_ALLOWED_HOSTS = input_with_default("PRODUCTION Allowed Hosts (comma separated)", "http://localhost:3000")
PROD_CORS_ALLOW_ALL_ORIGINS = input_with_default("PRODUCTION CORS Allow All Origins? (True/False)", "True")
PROD_CORS_ALLOWED_ORIGINS = input_with_default("PRODUCTION CORS Allowed Origins (comma separated)",
                                               "http://localhost:3000")

with open(".env", "w") as f:
    f.write(f"ENVIRONMENT={ENVIRONMENT}\n\n")

    f.write(f"DEV_DJANGO_PORT={DJANGO_PORT}\n")
    f.write(f"DEV_DB_NAME={DEV_DB_NAME}\n")
    f.write(f"DEV_DB_USER={DEV_DB_USER}\n")
    f.write(f"DEV_DB_PASSWORD={DEV_DB_PASSWORD}\n")
    f.write(f"DEV_DB_HOST={DEV_DB_HOST}\n")
    f.write(f"DEV_DB_PORT={DEV_DB_PORT}\n")
    f.write(f"DEV_CORS_ALLOWED_ORIGINS={DEV_CORS_ALLOWED_ORIGINS}\n")

    f.write(f"PRODUCTION_DJANGO_PORT={DJANGO_PORT}\n")
    f.write(f"PRODUCTION_DB_NAME={PROD_DB_NAME}\n")
    f.write(f"PRODUCTION_DB_USER={PROD_DB_USER}\n")
    f.write(f"PRODUCTION_DB_PASSWORD={PROD_DB_PASSWORD}\n")
    f.write(f"PRODUCTION_DB_HOST={PROD_DB_HOST}\n")
    f.write(f"PRODUCTION_DB_PORT={PROD_DB_PORT}\n")
    f.write(f"PRODUCTION_ALLOWED_HOSTS={PROD_ALLOWED_HOSTS}\n")
    f.write(f"PRODUCTION_CORS_ALLOW_ALL_ORIGINS={PROD_CORS_ALLOW_ALL_ORIGINS}\n")
    f.write(f"PRODUCTION_CORS_ALLOWED_ORIGINS={PROD_CORS_ALLOWED_ORIGINS}\n")

    f.close()


print(f"\n✅ .env file created with your settings. \n ")
