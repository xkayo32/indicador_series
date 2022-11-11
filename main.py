import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Manipulador(object):
    def __init__(self) -> None:
        self.stack: Gtk.Stack = Builder.get_object('stack')
        self.users = Users

    # Destroi oas janelas quando clica em fechar
    def on_main_window_destroy(self, Window):
        Gtk.main_quit()

    # Clicar em login
    def on_btn_login_clicked(self, button):
        email = self.__get_input('input_login_email')
        password = self.__get_input('input_login_password')
        self.__login(email, password)

    def on_btn_cadastrar_clicked(self, button):
        self.stack.set_visible_child_name('view_cadastro')

    def on_btn_esq_clicked(self, button):
        self.aviso = Builder.get_object('link_esq_aviso')
        self.aviso.set_text('')
        self.stack.set_visible_child_name('view_esqueci')

    def on_btn_esq_cancelar_clicked(self, button):
        self.aviso.set_text('')
        self.stack.set_visible_child_name('view_login')

    def on_btn_esq_enviar_clicked(self, button):
        consulta = self.users.filter(email=self.__get_input('btn_esq_email'))
        if consulta:
            self.aviso.set_text('Enviado com sucesso')
        else:
            self.aviso.set_text('Email não cadastrado')

        
    def on_btn_cad_salvar_clicked(self, button):
        name = self.__get_input('input_cad_name')
        email = self.__get_input('input_cad_email')
        password1 = self.__get_input('input_cad_password1')
        password2 = self.__get_input('input_cad_password2')
        self.__check_validadion(name,email, password1, password2)

    def on_btn_cad_cancelar_clicked(self, button):
        self.stack.set_visible_child_name('view_login')

    def __check_validadion(self, name:str,email: str, password1: str, password2: str) -> bool:
        if email and password1 == password2:
            self.users.create(name=name,email=email,password=password1)
            self.__msg_login(
                'Cadastro realizado', f'O email *{email}* foi cadastrado com sucesso.', 'dialog-ok')
            return True
        else:
            self.__msg_login(
                'Aviso', f'Erro ao tentar cadastrar o email *{email}*.', 'dialog-error')
            return False

    def __login(self, email: str, password: str):
        logando = self.users.filter(email=email,password=password)
        if logando:
            
            self.__msg_login(
                'Bem-Vindo', 'Usuario logado com sucesso', 'emblem-ok-symbolic')
        else:
            self.__msg_login(
                'Aviso', 'Email ou senha incorreto', 'dialog-error')

    def __get_input(self, id: str) -> str:
        return Builder.get_object(id).get_text()

    def __msg_login(self, title: str, body: str, icon: str) -> None:
        mensagem = Builder.get_object('msg_login')
        mensagem.props.text = title
        mensagem.props.secondary_text = body
        mensagem.props.icon_name = icon
        mensagem.show_all()
        mensagem.run()
        mensagem.hide()


Builder = Gtk.Builder()
Builder.add_from_file('ui.glade')
Builder.connect_signals(Manipulador())
Window: Gtk.Window = Builder.get_object('main_window')
Window.show_all()
Gtk.main()