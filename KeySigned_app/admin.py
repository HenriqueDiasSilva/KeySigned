from django.contrib import admin
from .models import UserChave, UserAssinatura, UserDocumento

class UserChaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_chave_privada', 'display_chave_publica')

    def display_chave_privada(self, obj):
        return obj.chave_privada.decode('utf-8')

    def display_chave_publica(self, obj):
        return obj.chave_publica.decode('utf-8')

    display_chave_privada.short_description = "Chave Privada"
    display_chave_publica.short_description = "Chave Pública"
admin.site.register(UserChave, UserChaveAdmin)

class UserAssinaturaAdmin(admin.ModelAdmin):
    list_display = ('data','hash', 'assinatura')
admin.site.register(UserAssinatura, UserAssinaturaAdmin)

class UserDocumentoAdmin(admin.ModelAdmin):
    list_display = ('user', 'texto')
admin.site.register(UserDocumento, UserDocumentoAdmin)
