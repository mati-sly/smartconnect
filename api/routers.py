class AuthRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'auth':
            return 'default'
        return 'smartconnect_db'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'auth':
            return 'default'
        return 'smartconnect_db'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'auth':
            return db == 'default'
        return db == 'smartconnect_db'
