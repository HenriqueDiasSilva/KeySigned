from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
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
            todas_assinaturas = UserAssinatura.objects.all()
            resultado = ""
            cont = 0
            for registro in todas_assinaturas:
                if registro.hash == request.POST['hash']:
                        resultado = "Este hash é referente a uma assinatura de um documento que foi assinado no sistema Key Signed"
                        return render(request, 'key_signed_app/home.html', {'hash':resultado})
            if cont == 0:
                resultado = "Este hash não consta em nosso sistema Key Signed"
            return render(request, 'key_signed_app/home.html', {'hash':resultado})
    
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
        if request.method == 'GET':
            documentos = UserDocumento.objects.filter(user=request.user)
            return render(request, 'key_signed_app/documentos.html', {'documentos':documentos})
        else:
            if request.method == 'POST':
                try:
                    usuario_chaves = UserChave.objects.get(user=user)
                    chave_publica_usuario = usuario_chaves.chave_publica

                    valor = request.POST['action']
                    id = ''.join(filter(str.isdigit, valor))
                    documentoDetalhe = UserDocumento.objects.get(pk=id)

                    public_key = RSA.import_key(chave_publica_usuario)
                    h = SHA256.new(documentoDetalhe.texto.encode())
                    
                    documentos = UserDocumento.objects.filter(user=request.user)
                    context = {
                        'documentos': documentos,
                    }

                    try:
                        pkcs1_15.new(public_key).verify(h, documentoDetalhe.assinado.assinatura)
                        context['validacao'] = "Esta assinatura é válida"
                        return render(request, 'key_signed_app/documentos.html', context)
                    
                    except:
                        context['validacao'] = "Esta assinatura é inválida"
                        return render(request, 'key_signed_app/documentos.html', context)
            
                except Exception as e:
                    print(e)
                    return redirect('documentos')

    else:
        return redirect('acesso')

def documentosTodosView(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            documentos = UserDocumento.objects.filter(assinado__isnull=False)
            return render(request, 'key_signed_app/documentosTodos.html', {'documentos':documentos})
        else:
            if request.method == 'POST':
                usuario_chaves = UserChave.objects.get(user=user)
                chave_publica_usuario = usuario_chaves.chave_publica

                valor = request.POST['action']
                id = ''.join(filter(str.isdigit, valor))
                documentoDetalhe = UserDocumento.objects.get(pk=id)

                public_key = RSA.import_key(chave_publica_usuario)
                h = SHA256.new(documentoDetalhe.texto.encode())

                documentos = UserDocumento.objects.filter(assinado__isnull=False)
                contexto = {
                    'documentos': documentos,
                }
                
                try:
                    pkcs1_15.new(public_key).verify(h, documentoDetalhe.assinado.assinatura)
                    contexto['validacao'] = "Esta assinatura pertence ao seu usuário"
                    return render(request, 'key_signed_app/documentosTodos.html', contexto)
                
                except:
                    contexto['validacao'] = "Esta assinatura não pertence ao seu usuário"
                    return render(request, 'key_signed_app/documentosTodos.html', contexto)


    else:
        return redirect('acesso')

def documentoView(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'key_signed_app/documento.html')
        else:
            if request.method == 'POST':
                try:
                    if request.POST['action'] == 'salvar':
                        documento = UserDocumento.objects.create(user=user, texto=request.POST['texto'], salvo=True, assinado=None)
                        documento.save()
                    else:
                        usuario_chaves = UserChave.objects.get(user=user)
                        chave_privada_usuario = usuario_chaves.chave_privada
                        
                        h = SHA256.new(request.POST['texto'].encode())
                        chave_RSA_privada = RSA.import_key(chave_privada_usuario)
                        assinatura= pkcs1_15.new(chave_RSA_privada).sign(h)
                        hash_hexa = h.hexdigest()
                        assinatura_usuario = UserAssinatura.objects.create(hash=hash_hexa,assinatura=assinatura)

                        documento = UserDocumento.objects.create(user=user, texto=request.POST['texto'], salvo=True, assinado=assinatura_usuario)
                        documento.save()
                    return redirect('documentos')
                except Exception as e:
                    print(e)
                    return render(request, 'key_signed_app/documento.html',{
                        'error': "Campos estão vazios"})
    else:
        return redirect('acesso')
    
def documentoDetalhesView(request, **kwargs):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            documentoDetalhe = UserDocumento.objects.get(pk=kwargs['documento_id'])
            documento_assinatura_hex = documentoDetalhe.assinado.assinatura.hex()
            return render(request, 'key_signed_app/documentoDetalhes.html',{'documento': documentoDetalhe, 'assinatura':documento_assinatura_hex})
        else:
            if request.method == 'POST':
                try:
                    usuario_chaves = UserChave.objects.get(user=user)
                    chave_privada_usuario = usuario_chaves.chave_privada
                    documento = UserDocumento.objects.get(pk=kwargs['documento_id'])
                    
                    h = SHA256.new(documento.texto.encode())
                    chave_RSA_privada = RSA.import_key(chave_privada_usuario)
                    assinatura= pkcs1_15.new(chave_RSA_privada).sign(h)
                    hash_hex = h.hexdigest()
                    assinatura_usuario = UserAssinatura.objects.create(hash=hash_hex,assinatura=assinatura)
                    
                    documento.assinado = assinatura_usuario
                    documento.save()
                    return redirect('documentos')
            
                except Exception as e:
                    print(e)
                    return redirect('documentos')
    else:
        return redirect('acesso')

def acessoView(request):
    return render(request, 'key_signed_app/acesso.html') 