import hashlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserChave, UserDocumento, UserAssinatura

def homeView(request):
    if request.method == 'GET':
        return render(request, 'key_signed_app/home.html')
    else:
        if request.method == 'POST':
            try:
                todas_assinaturas = UserAssinatura.objects.all()
                resultado = ""
                cont = 0
                for registro in todas_assinaturas:
                    if registro.assinatura == request.POST['hash']:
                         resultado = "Este hash é referente a uma assinatura de um documento que foi assinado no sistema Key Signed"
                         return render(request, 'key_signed_app/home.html', {'hash':resultado})
                if cont == 0:
                    resultado = "Este hash não consta em nosso sistema Key Signed"
                return render(request, 'key_signed_app/home.html', {'hash':resultado})
            except:   
                return render(request, 'key_signed_app/home.html',{
                    'error': "Campos estão vazios"})
    
def cadastrarView(request):
    if request.method == 'GET':
        return render(request, 'login/cadastrar.html',{
            'form': UserCreationForm})
    else:
        if request.method == 'POST':
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
                user.save()

                chave = RSA.generate(2048)
                chave_privada = chave.export_key()
                chave_publica = chave.publickey().export_key()

                user_chave = UserChave.objects.create(user=user, chave_privada=chave_privada, chave_publica=chave_publica)
                user_chave.save()

                login(request, user)
                return redirect('home')
            
            except:
                return render(request, 'login/cadastrar.html',{
                    'form': UserCreationForm,
                    'error': "Usuário já existe ou campos estão vazios"})

def entrarView(request):
    if request.method == 'GET':
        return render(request, 'login/entrar.html',{
            'form': AuthenticationForm})
    else:
        if request.method == 'POST':
            user = authenticate(
                request, username=request.POST['username'], password=request.POST['password'])

            if user is None:
                return render(request, 'login/entrar.html',{
                    'form': AuthenticationForm,
                    'error': "Usuário incorreto ou senha incorreta ou campos estão vazios"})

            else:
                login(request, user)
                return redirect('home')
            
def sairView(request):
    logout(request)
    return redirect('home')

def documentosView(request):
    user = request.user
    if user.is_authenticated:
        documentos = UserDocumento.objects.filter(user=request.user)
        return render(request, 'key_signed_app/documentos.html', {'documentos':documentos})
    else:
        return redirect('acesso')
    
def documentoView(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'key_signed_app/documento.html',{
                'form': UserCreationForm})
        else:
            if request.method == 'POST':
                try:
                    if request.POST['action'] == 'salvar':
                        documento = UserDocumento.objects.create(user=user, texto=request.POST['texto'], salvo=True, assinado=None)
                        documento.save()
                    else:
                        usuario_chaves = UserChave.objects.get(user=user)
                        chave_privada_usuario = usuario_chaves.chave_privada
                        
                        hash = hashlib.sha256(request.POST['texto'].encode()).digest()
                        chave_RSA = RSA.import_key(chave_privada_usuario)
                        cipher_RSA = PKCS1_OAEP.new(chave_RSA)
                        assinatura = cipher_RSA.encrypt(hash)
                        assinatura_texto = base64.b64encode(assinatura)
                        assinatura_usuario = UserAssinatura.objects.create(assinatura=assinatura_texto)

                        documento = UserDocumento.objects.create(user=user, texto=request.POST['texto'], salvo=True, assinado=assinatura_usuario)
                        documento.save()
                    return redirect('documentos')
                except Exception as e:
                    print(e)
                    return render(request, 'key_signed_app/documento.html',{
                        'form': UserCreationForm,
                        'error': "Campos estão vazios"})
    else:
        return redirect('acesso')
    
def documentoDetalhesView(request, **kwargs):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            documentoDetalhe = UserDocumento.objects.get(pk=kwargs['documento_id'])
            return render(request, 'key_signed_app/documentoDetalhes.html',{'documento': documentoDetalhe})
        else:
            if request.method == 'POST':
                try:
                    usuario_chaves = UserChave.objects.get(user=user)
                    chave_privada_usuario = usuario_chaves.chave_privada
                    documento = UserDocumento.objects.get(pk=kwargs['documento_id'])
                    
                    hash = hashlib.sha256(documento.texto.encode()).digest()
                    chave_RSA = RSA.import_key(chave_privada_usuario)
                    cipher_RSA = PKCS1_OAEP.new(chave_RSA)
                    assinatura = cipher_RSA.encrypt(hash)
                    assinatura_texto = base64.b64encode(assinatura)

                    assinatura_usuario = UserAssinatura.objects.create(assinatura=assinatura_texto)
                    
                    documento.assinado = assinatura_usuario
                    documento.save()
                    return redirect('documentos')
            
                except Exception as e:
                    print(e)
    else:
        return redirect('acesso')

def acessoView(request):
    return render(request, 'key_signed_app/acesso.html') 