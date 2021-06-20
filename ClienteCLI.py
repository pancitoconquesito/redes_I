import socket
import time
import os

HOST='ayredes.ddns.net'
PORTSMTP = 25
PORTPOP3 = 110
IPV  = socket.AF_INET
TCP  = socket.SOCK_STREAM


MAILFROM= '<root@dns.inf3340.inf>'
RCPT='<usuario@dns.inf3340.inf>'

class ClienteCLI():
    def __init__(self, host,portsmtp,portpop3,ipv,tcp):
        self.MAILFROM= MAILFROM
        self.RCPT=RCPT
        self.host=host
        self.portsmtp=portsmtp
        self.portpop3=portpop3
        self.ipv=ipv
        self.tcp=tcp
    # cierra la conexion del cliente con el servidor
    # @param: soc es el socket de la sesion
    def cerrarConexion(self, soc):
        self.enviar (soc, "QUIT")
        print(self.recibir(soc))
        soc.close()
    # envia mensaje al servidor, este necesita codificarse
    # @param: conexion es el socket de la sesion
    # @param: mensaje es el texto que se enviara al servidor
    def enviar (self, conexion, mensaje):
        msg = mensaje + '\r\n'
        conexion.send(msg.encode())
    # recibe respuesta de servidor, esta debe decodificarse
    # @param: conexion es el socket de la sesion
    # @return devuelve mensaje de respuesta del servidor
    def recibir (self, conexion):
        msg = conexion.recv(1024)
        return(msg.decode())
    # envia mensaje al servidor, la comprobacion es el numero que retorna el servidor
    # retorna la respuesta del servidor, en caso de exito retornará True (el exito se evalua con el numero de parametro comprobacion)
    # @param: conexion es el socket de la sesion
    # @param: mensaje es el texto que se enviará al servidor
    # @return retorna True en caso de comprobacion exitosa, False hubo error en la solicitud
    def enviarMensajeServidor(self, conexion, mensaje, comprobacion):
        self.enviar(conexion, mensaje)
        respuestaUSER = self.recibir(conexion)
        if respuestaUSER[:3] != comprobacion:
            #print(respuestaUSER)
            return False,respuestaUSER
        else:
            #print(respuestaUSER)
            return True,respuestaUSER
    # retorna un mensaje indicado con su numero, esta se ingresa desde parametro _id_
    # es necesario las fases de USER, PASS y LIST para que el servidor permita la consulta con RETR
    # si existe una falla retorno False como priemr parametro, el segundo es un string de error o un string con el mensaje solicitado
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @param _id_ es el numero de mensaje que se desea obtener
    # @return el primer parametro de retorno es un booleano que indica si el proceso fue exitoso, True en caso positivo, Falso si hubo error
    # @return el segundo parametro es un string que en caos de error avisa de este, mientras si el proceso es exitoso envia el textod el mensaje consultado
    def modoPOP3_particular(self, nombreUsuario,password,_id_):
        with socket.socket(self.ipv, self.tcp) as soc:
            print("\nIntentando conectar con ", HOST, ":", PORTPOP3,"...\n")
            # nos conectamos por el puerto de pop3 (110)
            soc.connect((self.host, self.portpop3))
            try:
                respuesta = self.recibir(soc)
                if respuesta[:3] == "+OK":
                    print(respuesta)
                if self.enviarMensajeServidor(soc,"USER " + nombreUsuario,"+OK")[0]:
                    if self.enviarMensajeServidor(soc, "PASS " + password, "+OK")[0]:
                        lista=self.enviarMensajeServidor(soc, "LIST" , "+OK")
                        if lista[0]:
                            return self.enviarMensajeServidor(soc, "RETR " + _id_, "+OK")[1]
                self.cerrarConexion(soc)
            except:
                self.cerrarConexion(soc)
                return False,"No se pudo conectar al servidor, F\n"
        return False,"No se pudo conectar al servidor, F\n"
        
    # elimina todo el correo del servidor
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @param _id_ es el numero de mensaje que se desea obtener
    def modoPOP3_eliminarTodoCorreo(self, nombreUsuario,password) :
        total=len(self.obtenerListaID(nombreUsuario,password))
        for i in range(0,total):
            self.modoPOP3_eliminar(nombreUsuario,password,'1')
    # elimina un correo en especifico, esta se indica con su numero pasado por el parametro _id_
    # para eliminar se utiliza DELE
    # en caso de error retorna como primer parametro un False
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @param _id_ es el numero de mensaje que se desea obtener
    # @return el primer parametro de retorno es un booleano que indica si el proceso fue exitoso, True en caso positivo, Falso si hubo error
    # @return el segundo parametro es un string que en caos de error avisa de este
    def modoPOP3_eliminar(self, nombreUsuario,password,_id_):
        with socket.socket(self.ipv, self.tcp) as soc:
            print("\nIntentando conectar con ", HOST, ":", PORTPOP3,"...\n")
            # nos conectamos por el puerto de pop3 (110)
            soc.connect((self.host, self.portpop3))
            try:
                respuesta = self.recibir(soc)
                if respuesta[:3] == "+OK":
                    print(respuesta)
                if self.enviarMensajeServidor(soc,"USER " + nombreUsuario,"+OK")[0]:
                    if self.enviarMensajeServidor(soc, "PASS " + password, "+OK")[0]:
                        self.enviarMensajeServidor(soc, "DELE "+_id_, "+OK")
                self.cerrarConexion(soc)
            except:
                self.cerrarConexion(soc)
                return False,"No se pudo conectar al servidor, F\n"
        return False,"No se pudo conectar al servidor, F\n"
    # obtiene lista de mensajes, de esta obtiene solo subject y to
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @return retorna un vector de string con el 'subject' y 'to' de cada mensaje del buzon
    def modoPOP3_listaSubject(self, nombreUsuario,password):
        lista=[]
        isError=False
        resultado=self.obtenerListaID(nombreUsuario,password) 
        for res in resultado:
            cosa=self.modoPOP3_particular(nombreUsuario,password,res)
            cosa=cosa.split(sep='\n')
            try:
                lista.append('Subject :  '+cosa[8]+'       To:   '+cosa[10])
            except:
                lista.append('Subject :  '+cosa[6]+'       To:   '+cosa[8])
        return lista
    # obtiene respuesta LIST de mensajes, de esta retorna solo el id
    # a pesar que los id son el indice actual de los mensajes en el servidor,
    # nos aseguramos de obtenerlo y no deducirlo con return np.array(range(1,(len(resultado)+1)))
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @return vector de string con todos los id de los mensajes del buzon
    def obtenerListaID(self, nombreUsuario,password):
        resultado=self.modoPOP3(nombreUsuario,password)[1]
        resultado=resultado.split(sep='\r\n')
        resultado=resultado[1:-2]
        resultadoRetorno=[]
        for i in range(0,len(resultado)):
            resultado[i] =resultado[i].split(sep=' ')
            resultadoRetorno.append(resultado[i][0])
        return resultadoRetorno
    # modo pop3 base, restorna la respuesta LIST del servidor
    # @param: nombreUsuario es el nombre de usuario, en este contexto debe ser 'usuario'
    # @param: password es la clave de acceso, en este contexto debe ser 'usuario'
    # @return el primer parametro de retorno es un booleano que indica si el proceso fue exitoso, True en caso positivo, Falso si hubo error
    # @return el segundo parametro es un string que en caos de error avisa de este
    def modoPOP3(self, nombreUsuario,password):
        with socket.socket(self.ipv, self.tcp) as soc:
            print("\nIntentando conectar con ", HOST, ":", PORTPOP3,"...\n")
            # nos conectamos por el puerto de pop3 (110)
            soc.connect((HOST, PORTPOP3))
            try:
                respuesta = self.recibir(soc)
                if respuesta[:3] == "+OK":
                    print(respuesta)
                if self.enviarMensajeServidor(soc,"USER " + nombreUsuario,"+OK")[0]:
                    if self.enviarMensajeServidor(soc, "PASS " + password, "+OK")[0]:
                        lista=self.enviarMensajeServidor(soc, "LIST" , "+OK")
                        if lista[0]:
                            return True,lista[1]
                        else:
                            return "Ha ocurrido un error, intente nuevamente"
                self.cerrarConexion(soc)
            except:
                self.cerrarConexion(soc)
                return False,"No se pudo conectar al servidor, F\n"
        return False,"No se pudo conectar al servidor, F\n"
    # envia el cuerpo del mensaje, la que se compone de los parametros, salvo comprobacion, esta es para comparar la respuesta de exito retornada por el servidor
    # por cada mensaje realizado
    # @param: conexion es el socket de la sesion
    # @param: subject es el titulo del mensaje
    # @param: fromText es el nombre del origen
    # @param: toText es el nombre del destinatario
    # @param: mensaje es el texto que se enviará en el correo
    # @param: comprobacion es el codigo que discrimina con la respuesta del servidor el caso de exito del proceso
    # @param: retorna False si falla el enviod el cuerpo del mensaje, True en casod e exito
    def enviarCuerpo(self, conexion,subject,fromText,toText,mensaje,comprobacion):
        #ordenamos la secuencia y lo enviamos al servidor
        cuerpo=([subject,fromText,toText,"\n",mensaje,"","."])
        for i in range(0,7):
            self.enviar(conexion, cuerpo[i])
        #obtenemos respuesta del servidor
        return False if self.recibir(conexion)[:3]!=comprobacion else True
    # metodo para enviar mensaje, puede enviar un correo a multiples destinatarios, para ello solo es necesario
    # separar la direccion por comas, no existe problema con la presencia de espacios antes o despues.
    # @param: subject es el titulo del mensaje
    # @param: fromText es el nombre del origen
    # @param: toText es el nombre del destinatario
    # @param: mensaje es el texto que se enviará en el correo
    # @param: comprobacion es el codigo que discrimina con la respuesta del servidor el caso de exito del proceso
    # @return: string que indica que hubo un error o que el mensaje fue enviado exitosamente
    def modoSMTP(self, subject,fromText,toText,mensaje,comprobacion):
        #toText es un string formato "correoA@gmail.com, bla@gmail.com ,co3gmail.com" 
        #elimina todos los espacios
        toText=toText.replace(" ", "")
        #separa cada correo y forma vector de correos
        toText=toText.split(sep=',')
        # se envia mensaje a cada correo ingresado
        mensajeRetorno=''
        # en cada iteracion se envia un correo a un destinatario
        for i in range(0,len(toText)):
            with socket.socket(self.ipv, self.tcp) as soc:
                print("\nIntentando conectar con ", self.host, ":", self.portsmtp,"...\n")
                # nos conectamos por el puerto de smtp (25)
                soc.connect((HOST, PORTSMTP))
                try:
                    respuesta = self.recibir(soc)
                    if respuesta[:3] == "220":
                        print(respuesta)
                        if self.enviarMensajeServidor(soc,"HELO " + "192.168.0.9", "250")[0]:
                            if self.enviarMensajeServidor(soc,"MAIL FROM: <root@dns.inf3340.inf>", "250")[0]:
                                if self.enviarMensajeServidor(soc, "RCPT TO: <usuario@dns.inf3340.inf>", "250")[0]:
                                    if self.enviarMensajeServidor(soc, "DATA", "354")[0]:
                                        if self.enviarCuerpo(soc,subject,fromText,toText[i],mensaje,comprobacion):
                                            mensajeRetorno=mensajeRetorno+'MENSAJE ENVIADO EXITOSAMENTE PARA : '+toText[i]+"\n"
                                        else :
                                            mensajeRetorno=mensajeRetorno+"Ha ocurrido un error enviando cuerpo mensaje, intente nuevamente\n"
                                    else:
                                        mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase DATA, intente nuevamente\n"
                                else:
                                    mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase RCPT, intente nuevamente\n"
                            else:
                                mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase MAIL FROM:, intente nuevamente\n"
                        else:
                            mensajeRetorno=mensajeRetorno+"AHa ocurrido un error en fase HELO, intente nuevamente\n"
                    self.cerrarConexion(soc)
                except:
                    self.cerrarConexion(soc)
                    mensajeRetorno= mensajeRetorno+"No se pudo conectar al servidor, F\n"
        return mensajeRetorno
    # es igual que el metodo modoSMTP mas la logica del uso de parametros extras, 
    # estos parametros no deben modificarse en este contexto, solo estan creadas por motivos de practica
    # metodo para enviar mensaje, puede enviar un correo a multiples destinatarios, para ello solo es necesario
    # separar la direccion por comas, no existe problema con la presencia de espacios antes o despues. 
    # @param: mailFrom en este contexto por defecto es '<root@dns.inf3340.inf>', en caso de cambiarse producirá error
    # @param: rcpt en este contexto por defecto es '<usuario@dns.inf3340.inf>', en caso de cambiarse producirá error
    # @param: subject es el titulo del mensaje
    # @param: fromText es el nombre del origen
    # @param: toText es el nombre del destinatario
    # @param: mensaje es el texto que se enviará en el correo
    # @param: comprobacion es el codigo que discrimina con la respuesta del servidor el caso de exito del proceso
    # @return: string que indica que hubo un error o que el mensaje fue enviado exitosamente
    def modoSMTP2(self, mailFrom,rcpt,subject,fromText,toText,mensaje,comprobacion):
        # si no se modificaron asignandole valores, se utilizaran los valores por defectos que si funcionan
        if len(mailFrom)==0:
            mailFrom=self.MAILFROM
        if len(rcpt)==0:
            rcpt=self.RCPT
        #toText es un string formato "correoA@gmail.com, bla@gmail.com ,co3gmail.com" 
        #elimina todos los espacios
        toText=toText.replace(" ", "")
        #separa cada correo y forma vector de correos
        toText=toText.split(sep=',')
        # se envia mensaje a cada correo ingresado
        mensajeRetorno=''
        for i in range(0,len(toText)):
            with socket.socket(self.ipv, self.tcp) as soc:
                print("\nIntentando conectar con ", self.host, ":", self.portsmtp,"...\n")
                # nos conectamos por el puerto de smtp (25)
                soc.connect((HOST, PORTSMTP))
                try:
                    respuesta = self.recibir(soc)
                    if respuesta[:3] == "220":
                        print(respuesta)
                        if self.enviarMensajeServidor(soc,"HELO "+socket.gethostbyname('localhost'), "250")[0]:
                            if self.enviarMensajeServidor(soc,"MAIL FROM: "+ mailFrom, "250")[0]:
                                if self.enviarMensajeServidor(soc, "RCPT TO: "+rcpt, "250")[0]:
                                    if self.enviarMensajeServidor(soc, "DATA", "354")[0]:
                                        if self.enviarCuerpo(soc,subject,fromText,toText[i],mensaje,comprobacion):
                                            mensajeRetorno=mensajeRetorno+'MENSAJE ENVIADO EXITOSAMENTE PARA : '+toText[i]+"\n"
                                        else :
                                            mensajeRetorno=mensajeRetorno+"Ha ocurrido un error enviando cuerpo mensaje, intente nuevamente\n"
                                    else:
                                        mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase DATA, intente nuevamente\n"
                                else:
                                    mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase RCPT, revise Pestaña Configuración intente nuevamente\n"
                            else:
                                mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase MAIL FROM:, revise Pestaña Configuración intente nuevamente\n"
                        else:
                            mensajeRetorno=mensajeRetorno+"Ha ocurrido un error en fase HELO, revise Pestaña Configuración e intente nuevamente\n"
                    self.cerrarConexion(soc)
                except:
                    self.cerrarConexion(soc)
                    mensajeRetorno= mensajeRetorno+"No se pudo conectar al servidor, F\n"
        return mensajeRetorno
