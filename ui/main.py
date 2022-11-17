import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Validacao:
    def __init__(self): 
        pass
    
    @staticmethod
    def validando_senhas_cadastro(senha1:str,senha2:str) -> bool:
        if not senha1 == senha2:
            return False
        return True
    
    @staticmethod
    def validando_senha_login(banco:dict,usuario:str,senha:str) -> bool:
        if banco[usuario.lower()] == senha:
            return True
        return False
    
    @staticmethod
    def validando_usuario(banco:dict,usuario:str) -> bool:
        if usuario.lower() in banco.keys():
            return True
        return False

class Manipulador(Validacao):
    def __init__(self) -> None:
        super().__init__()
        self.stack: Gtk.Stack = Builder.get_object('stack')
        self.dados_armazenado:dict = {}
        
    def banco_dados(self,usuario:str,senha:str):
        self.dados_armazenado.update({usuario:senha})
        
    # Destroi oas janelas quando clica em fechar
    def on_main_window_destroy(self, Window):
        Gtk.main_quit()

    def on_btn_logar_clicked(self,button):
        self.stack.set_visible_child_name('view_buscar')

        # usuario = Builder.get_object('input_email_login').get_text()
        # if self.validando_usuario(self.dados_armazenado,usuario):
        #     password = Builder.get_object('input_password_login').get_text()
        #     if self.validando_senha_login(self.dados_armazenado,usuario,password):
        #         self.stack.set_visible_child_name('view_buscar')
        #     else:
        #         print(f'Login failed! Password incorrect')
        # else:
        #     print(f'Usuario não encontrado')

    def on_btn_cadastrar_clicked(self,button):
        self.stack.set_visible_child_name('view_cadastro')
       
    def on_btn_salvar_clicked(self,button):
        usuario = Builder.get_object('input_email_cad')
        if not self.validando_usuario(self.dados_armazenado, usuario.get_text()):
            senha1 = Builder.get_object('input_password1_cad')
            senha2 = Builder.get_object('input_password2_cad')
            if self.validando_senhas_cadastro(senha1.get_text(),senha2.get_text()):
                self.banco_dados(usuario.get_text(),senha1.get_text())
                senha1.set_text('')
                senha2.set_text('')
                usuario.set_text('')
                print(f'Salvo com sucesso')
            else:
                print(f'Senha diferentes')
        else:
            print(f'Usuario ja cadastrado')
                  
    def on_btn_voltar_clicked(self,button):
        self.stack.set_visible_child_name('view_login')
        
    def on_btn_buscar_clicked(self,button):
        acao = Builder.get_object('combo_acao')
        data_inicial = Builder.get_object('input_dt_inicial').get_text()
        data_final = Builder.get_object('input_dt_final').get_text()
        print(data_inicial, data_final, acao)
    

Builder = Gtk.Builder()
Builder.add_from_file('ui/app_ui.glade')
Builder.connect_signals(Manipulador())
Window: Gtk.Window = Builder.get_object('main_window')
Window.show_all()
Gtk.main()