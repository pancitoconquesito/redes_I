from PyQt5 import QtWidgets, uic
import sys
# enlazamos la clase CLienteCLI
from ClienteCLI import *

class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui',self)
        #instanciamos a cliente
        self.cliente=ClienteCLI(HOST,PORTSMTP,PORTPOP3,IPV,TCP)
        #agregamos accion de click a los botones
        self.botonSend.clicked.connect(lambda:self.crearMail())
        self.botonLogin.clicked.connect(lambda:self.verCorreo())
        self.botonCleanSMTP.clicked.connect(lambda:self.limpiarOutSMPT())
        self.list.clicked.connect(lambda:self.mostrarMensajeEnPantalla())
        self.botonDelete.clicked.connect(lambda:self.eliminarCorreo())
        self.botonDeleteAll.clicked.connect(lambda:self.eliminarTodoCorreo())
        #valores por defectos de atributos
        self.OUTPUT_smtp='- Completa los datos y envia un correo -\n'
        self.outputSMTP.setPlainText(self.OUTPUT_smtp)
        self.userUlt=None
        self.passUlt=None
        self.infoDisponible=False
        self.helo=''
        self.mailFrom=''
        self.rcpt=''
        self.textTotal.setText('Identificate...')

    # refresca la la pantalla de la pestaña Revisar Buzon
    # esto ocurre al querer ver la lista de mensajes o al eliminar alguno
    def refrescar(self):
        self.list.clear()
        self.textMensajeFinal.setPlainText('')
        elementos=self.cliente.modoPOP3_listaSubject(self.userUlt,self.passUlt)
        for elemento in elementos:
            self.list.addItem(elemento)
        self.textTotal.setText('Total correos : '+str(len(elementos)))
        if len(elementos)==0 and self.cliente.modoPOP3(self.userUlt,self.passUlt)[0]==False:
            self.textTotal.setText('Error en conexión.')
    # elimina todos los mensajes del buzon
    def eliminarTodoCorreo(self):
        if self.infoDisponible:
            self.cliente.modoPOP3_eliminarTodoCorreo(self.userUlt,self.passUlt)
            self.refrescar()
    # elimina un mensaje seleccionado
    def eliminarCorreo(self):
        indice=self.list.currentRow()
        if self.userUlt!=None and self.passUlt!=None and indice!=-1:
            self.cliente.modoPOP3_eliminar(self.userUlt,self.passUlt,str(indice+1))
            self.refrescar()
    # muestra el contenido del mensaje seleccionado en pestaña Revisar Buzon
    def mostrarMensajeEnPantalla(self):
        # obtengo el indice de la lista que estoy seleccionando
        indice=self.list.currentRow()
        if self.userUlt!=None and self.passUlt!=None:
            # le doy formato al mensaje
                # aqui separamos el mensaje por cada linea
            mensajeSeleccionado=self.cliente.modoPOP3_particular(self.userUlt,self.passUlt,str(indice+1))
            textoFinal=mensajeSeleccionado.split(sep='\n')
            try: 
                infoExtra=textoFinal[1:8]
                # el join es para pasar de array a string
                infoExtra="".join(infoExtra)
                # la posicion 13 es cuando comienza el mensaje, esta termina en la antepenultima linea ([-3])
                mensajeFinal=textoFinal[13:-3]
                mensajeFinal[0]='\r|\t'+mensajeFinal[0]
                # tabulamos el mensaje
                for i in range(0,len(mensajeFinal)):
                    mensajeFinal[i]='\r|\t'+mensajeFinal[i]
                mensajeFinal = "".join(mensajeFinal)
                # formato terminado
                textoFinal=infoExtra+'__________________________________________________\n\n'+'FROM : '+textoFinal[9]+'\n'+"Mesagge : \n "+mensajeFinal+'\n__________________________________________________\n'
                self.textMensajeFinal.setPlainText(textoFinal)
            except:
                # en caso de error muestra el mensaje sin formato especifico
                self.textMensajeFinal.setPlainText(mensajeSeleccionado)
    # revisa si existen campos vacios en la pestaña Enviar Correo
    # @param: elementos son una coleccion con la lectura de los campos que se desea comprobar si esta vacio
    # @return True en caso de tener algun campo vacio, False si todos los campos estan rellenos
    def camposVacios(self,elementos):
        for elemento in elementos:
            if elemento=='':
                return True
        return False
    # limpia los campos de la pestaña Enviar Correo
    def limpiarOutSMPT(self):
        self.OUTPUT_smtp='- Completa los datos y envia un correo -\n'
        self.outputSMTP.setPlainText(self.OUTPUT_smtp)
    # actualiza los valores ingresados en la pestaña de configuracion para parametros extra de SMTP
    def loadExtraParametros(self):
        self.helo=self.Texthelo.text()
        self.mailFrom=self.TextMailFrom.text()
        self.rcpt=self.TextRCPT.text()
    # Crea de uno a muchos correos, esta se llama al presionar el boton de enviar en pestaña Enviar correo
    def crearMail(self):
        _subject_=self.textSubject.text()
        _from_=self.textFrom.text()
        _to_=self.textTo.text()
        _message_=self.textMessage.toPlainText()
        campos=([_subject_,_from_,_to_,_message_])
        # revisa que todos los campos esten completados
        if(self.camposVacios(campos)==False):
            self.OUTPUT_smtp=self.OUTPUT_smtp+"Enviando Mensaje...\n"
            self.outputSMTP.setPlainText(self.OUTPUT_smtp)
            self.loadExtraParametros()
            #respuestServidor=self.cliente.modoSMTP(_subject_,_from_,_to_,_message_,"250")  # version sin configuracion extra
            respuestServidor=self.cliente.modoSMTP2(self.helo,self.mailFrom,self.rcpt,_subject_,_from_,_to_,_message_,"250")
            self.OUTPUT_smtp=self.OUTPUT_smtp+respuestServidor
            self.textSubject.setText('')
            self.textFrom.setText('')
            self.textTo.setText('')
            self.textMessage.setPlainText('')
        else:
            self.OUTPUT_smtp=self.OUTPUT_smtp+"Error. Completa todos los campos.\n"
        self.outputSMTP.setPlainText(self.OUTPUT_smtp)
    # enlista los correos existentes, estas pueden ser seleccionadas para ver su contenido, es necesario identificarse antes, esto ocurre en la pestaña Revisar Correo
    def verCorreo(self):
        _user_=self.textUser.text()
        _password_=self.textPassword.text()
        campos=([_user_,_password_])
        #reviso si tengo completos los campos
        if(self.camposVacios(campos)==False):
            self.userUlt=_user_
            self.passUlt=_password_
            self.infoDisponible=True
            #refresco pantalla de ui y muestro los correos
            self.refrescar()
        else:
            self.textTotal.setText('Error, rellena todos los campos...')
            self.infoDisponible=False

# instanciamos la UI
app=QtWidgets.QApplication(sys.argv)
ventanasApp=UI()
# se inicializa
ventanasApp.show()
app.exec()
sys.exit(ventanasApp.exec_())

