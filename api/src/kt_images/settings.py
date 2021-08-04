import kt_images.base_settings as settings

class Settings(settings.BaseSettings):
    app_description = 'Images http storage backend.'
    app_settings = (
        settings.api_endpoint,
        settings.postgres_dsn,
        settings.postgres_arraysize,
        settings.uploads_dir
    )
