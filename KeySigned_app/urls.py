from django.contrib import admin
from django.urls import path
from KeySigned_app.views import homeView, cadastrarView, entrarView, sairView, documentosView, acessoView, documentoView, documentoDetalhesView, documentosTodosView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homeView, name='home'),
    path('cadastrar/', cadastrarView, name='cadastrar'),
    path('entrar/', entrarView, name='entrar'),
    path('sair/', sairView, name='sair'),
    path('documentos/', documentosView, name='documentos'),
    path('documentos/todos', documentosTodosView, name='documentosTodos'),
    path('documento/', documentoView, name='documento'),
    path('acesso/', acessoView, name='acesso'),
    path('documento/<int:documento_id>/',
         documentoDetalhesView, name="documentoDetalhes"),
]
