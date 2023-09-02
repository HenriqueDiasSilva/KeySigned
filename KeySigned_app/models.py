from django.db import models
from django.contrib.auth.models import User

class UserChave(models.Model):
    class Meta:
        verbose_name = 'Chave do Usuário'
        verbose_name_plural = 'Chave do Usuários'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userChave')
    chave_privada = models.BinaryField(verbose_name='Chave Privada')
    chave_publica = models.BinaryField(verbose_name='Chave Pública')

    def __str__(self):
        return self.user.username

class UserAssinatura(models.Model):
    class Meta:
        verbose_name = 'Assinaturas do Usuário'
        verbose_name_plural = 'Assinaturas do Usuários'

    data = models.DateTimeField(verbose_name='Data e Hora', auto_now_add=True)
    hash = models.TextField(verbose_name='Hash')
    assinatura = models.BinaryField(verbose_name='Assinatura')

    def __str__(self):
        data_formatada = self.data.strftime('%Y-%m-%d %H:%M:%S')
        return data_formatada

class UserDocumento(models.Model):
    class Meta:
        verbose_name = 'Documento do Usuário'
        verbose_name_plural = 'Documentos do Usuários'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userDocumento')
    texto = models.TextField(verbose_name='Texto')
    salvo = models.BooleanField(verbose_name='Foi salvo?')
    assinado = models.ForeignKey(UserAssinatura, on_delete=models.CASCADE, related_name='assinaturaUser', null=True, blank=True)

    def __str__(self):
        return self.user.username
