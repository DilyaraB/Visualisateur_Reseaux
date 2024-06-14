# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Ce n'est pas le projet final. Il faut pas utiliser ce fichier. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# C'est une version du code à executer si la librairie Tkinter continue a causer des erreurs apres son installation.
# Cette version n'affiche pas d'interface graphique, mais elle cree le fichier resultat de visualisateur. 
# Notre programme original est le fichier visualisateur.py



#capture des trames 
import sys
import os

#from contextlib import suppress

from tkinter import *
from tkinter import ttk
import random

#VARIABLES GLOBALES
ORDRE = 1
MAXMSG=50

########################################################################
########################### LES CLASSES ################################
########################################################################
class TCP:
    def __init__(self,psrc,pdst,seq,ack,len,flags,win,msg):
        self.portSrc = psrc
        self.portDst = pdst
        self.seq = seq
        self.ack = ack
        self.len = len
        self.win = win
        self.flags = flags 
        self.msg = msg
        self.HTTP = False
    

    def findServer(self):
        """ renvoie 0 serveur est la source et 1 si serveur est le client."""
        if (self.portSrc==80):
            return 0
        elif (self.portDst==80):
            return 1
        else:
            return -1
    
    #On veut juste etre sur ici.
    def isThereHTTP(self):
        if(self.msg!=""):
            possibilities = ["GET","HEAD","POST","OPTIONS","PUT","CONNECT","TRACE","PATCH","DELETE","HTTP"]
            for p in possibilities:
                if (p in self.msg):
                    self.HTTP=True

    #a horrible but necessary function to check all the flags
    def printFlags(self):
        morethan1 = False
        res = "["
        if(str(self.flags[5])=="1"):
            res+="FIN"
            morethan1=True
        if(self.flags[4]=='1'):
            if (morethan1):
                res+=", "
            res+="SYN"
            morethan1=True
        if(self.flags[3]=='1'):
            if (morethan1):
                res+=", "
            res+="RST"
            morethan1=True
        if(self.flags[2]=='1'):
            if (morethan1):
                res+=", "
            res+="PSH"
            morethan1=True
        if(self.flags[1]=='1'):
            if (morethan1):
                res+=", "
            res+="ACK"
            morethan1=True
        if(self.flags[0]=='1'):
            if (morethan1):
                res+=", "
            res+="URG"
            morethan1=True
        res+="]"
        return res

    def toStringTCP(self):
        self.isThereHTTP()
        if(not self.HTTP):
            affichage=str(self.portSrc)+" -> "+str(self.portDst)+" "+self.printFlags()+" Seq="+str(self.seq)+" Ack="+str(self.ack)+" Win="+str(self.win)
            if (len(affichage)>60):
                return f"{' ':^52}{'TCP: '}"+affichage[:60]
            return f"{' ':^52}{'TCP: '}"+affichage
        else :
            affichage=self.msg.split('\r\n')[0]
            if (len(affichage)>60):
                return f"{' ':^52}{'HTTP: '}"+self.msg.split('\r\n')[0][:60]
            return f"{' ':^52}{'HTTP: '}"+self.msg.split('\r\n')[0]
                           
class IP:
    def __init__(self,adst,asrc,len,protocol,tcp : TCP):
        self.dest = adst
        self.src = asrc
        self.len = len 
        self.protocol = protocol
        self.tcp=tcp
    
    def printIP(self):
        print(self.src+"->"+self.dest)

    #si le serveur est la source alors la fonction renvoie l'@ IP src contenu dans le paquet IP et l'@ dest sinon
    def findServer(self):
        valeur = self.tcp.findServer()
        if (valeur==-1):
            return None
        if (valeur==0):
            return self.src
        else:
            return self.dest
    #si le client est la source alors la fonction renvoie l'@ IP src contenu dans le paquet IP et l'@ dest sinon
    
    def findClient(self):
        valeur = self.tcp.findServer()
        if (valeur==1):
            return self.src
        else:
            return self.dest

    def findClientPort(self):
        val=self.tcp.findServer()
        if(val==0): #src==serveur
            return self.tcp.portDst
        elif(val==1):
            return self.tcp.portSrc
    
    def toStringIP(self):
        if(self.tcp==None):
            #jamais le cas car on le filtre dans la fonction qui lit la trame.
            print("There is no TCP packet in this frame. Exiting program")
            sys.exit()
        else:
            return self.tcp.toStringTCP()

class Ethernet:
    def __init__(self,md,ms,type,ip : IP):
        self.macDst = md
        self.macSrc = ms
        self.type = type
        self.len = 14
        self.ip = ip
    
    def toStringEth(self):
        if(self.ip==None):
            print("There is no IP packet in this frame. Exiting program")
            sys.exit()
        else:
            return self.ip.toStringIP()

class Trame: 
    def __init__(self,eth : Ethernet):
        self.eth=eth
        self.ipServer=None 
        self.ipClient=None

        #obligatoire d'initialiser les adresses ip avec la fonction ClientServeur

        self.findClientServeur()

    def findClientServeur(self):
        #if portSrc=80 then src = server et dst = client
        if (self.eth.ip.tcp.portSrc==80) :
            self.ipServer=self.eth.ip.src
            self.ipClient=self.eth.ip.dest
        #if portDst=80 then src = client et dst = serveur   
        elif(self.eth.ip.tcp.portDst==80) :
            self.ipServer=self.eth.ip.dest
            self.ipClient=self.eth.ip.src
        else:
            self.ipServer=None
            
    def printTrame(self):
        global ORDRE
        res = self.eth.toStringEth()+'\n' #affiche les valeurs importants : msg http ou tcp

        #le sens de fleche : 
        # si @src==ipServeur alors la fleche est vers la gauche <---
        # sinon alors la fleche est vers la droite --->

        #si msg de server vers client   
        IPClient = (self.eth.ip.findClient())
        portClient = str(self.eth.ip.findClientPort())
        IPServeur = (self.eth.ip.findServer())
        if IPServeur==None:
            return None
        
        serv = "80"
        if (self.eth.ip.dest==self.ipServer):
            arrow = " | ------------------------------------------------------------------> | "
            res+=f"{str(ORDRE):^5}{IPClient:^25}{portClient:^20}{arrow}{serv:^20}{IPServeur:^25}"+'\n'

        #si msg de client vers serveur
        else:
            arrow = " | <------------------------------------------------------------------ | "
            res+=f"{str(ORDRE):^5}{IPClient:^25}{portClient:^20}{arrow}{serv:^20}{IPServeur:^25}" +'\n'
            
        return res

class Flux:
    def __init__(self,listTrames : Trame):
        self.trames=listTrames
        #pour initialiser les portes et les adresses IP on regarde le premier
        #trame 
        if(len(self.trames)<1):
            print("Aucune trame avec un protocol TCP capturée.")
            sys.exit()
        

    def writeSortie(self):
        res = ""
        res += f"{'ordre':<5}{'@_IP_client':^25}{'port_client':^20}{'informations':^72}{'port_serveur':^20}{' @_IP_serveur':^25}"+"\n"
        res+=self.printTrames()
        #print(res)
        return res

    def printTrames(self):
        global ORDRE
        res=""
        for t in self.trames:
            if t.ipServer==None:
                print("Cette trame ne contient pas un protocole TCP avec un port serveur = 80. Le programme ignorera cette trame et continuera.")
            tr = t.printTrame()
            if tr!= None:
                res+=tr+'\n'
                ORDRE+=1
        return res
        

########################################################################
##################### FONCTIONS DU PROGRAMME ###########################
########################################################################

#lire un fichier et extraire une liste des trames
def readFile(filename):
    try:
        fichier = open(filename,"r")
    except OSError:
        print("Fichier "+filename+" n'existe pas ou n'est pas un fichier text. Fin du programme.")
        sys.exit()
    with fichier:
        try:
            lignes = fichier.readlines() #liste contenant les lignes du fichier
                #print(lignes)
            trames = []

            for l in lignes:
                if (l!='\n'): #if ligne exists

                    parts = l.split("   ") #partie offset et les bytes
                    offset = parts[0]
                    #si nouvelle trame alors on cree une nouvelle trame (vide) et l'ajoute dans la liste des trames
                    if (offset=="0000"):
                        trame = ""
                        if (len(trames)>9999):
                            print("Entree de +10000 trames. Le programme utilisera les 10000 premieres trames. Nous sommes desolees.")
                            break
                        trames.append(trame)
                    bytes = parts[1].split()
                    #ajoute du contenu hex(=trame) dans la liste
                    for b in bytes:
                        trames[-1]+=b
        except (ValueError,IndexError):
            print("Mauvais format de fichier. Le programme visualise des fichier contenant des hexdumps. Fin du programme.")
            sys.exit()
        fichier.close()
        return trames


#FONCTION POUR LE FILTRAGE D'UNE TRAME 
#(ici trame n'appartient pas a la classe Trame. elle est de type String dans la liste des trames lue par la fonction readFile())
def tramReader(trame):
    #DISCLAIMER : this function is horrible to look at

    #on commence avec Ethernet parce que pourquoi pas
    #Creation de l'Ethernet de notre trame
    try:
        macsrc = trame[0:6*2] 
        macdst = trame[6*2:12*2]
        type = trame[12*2:14*2] #on suppose que vous avez mis les bonnes valeurs pour le type

        e = Ethernet(macdst,macsrc,type,None) #on ajoutera ip apres sa creation

        #creation du paquet ip
        #si la trame est incomplet et ne contient pas HL
        HL = int(trame[29])*4 #HEADER LENGTH -> LENGTH OF IPs 30ieme char dans trame


        adsrc = str(int(trame[26*2:27*2],16))+"."+str(int(trame[27*2:28*2],16))+"."+str(int(trame[28*2:29*2],16))+"."+str(int(trame[29*2:30*2],16))
        addst = str(int(trame[30*2:31*2],16))+"."+str(int(trame[31*2:32*2],16))+"."+str(int(trame[32*2:33*2],16))+"."+str(int(trame[33*2:34*2],16)) 
        protocol = int(trame[46:48],16)
        

        #si paquet IP contient un autre protocole on quitte le programme
        if (protocol!=6):
            print("La trame contient un autre protocole que TCP.  Le programme ignorera cette trame et continuera.")
            return None

        ip = IP(addst,adsrc,HL,protocol,None)
        e.ip=ip

        #tcp
        debutTCP = 2*(e.len+e.ip.len)
        psrc = int(trame[debutTCP:debutTCP+4],16)
        pdst = int(trame[debutTCP+4:debutTCP+8],16)
        seq = int(trame[debutTCP+8:debutTCP+16],16) 
        ack = int(trame[debutTCP+16:debutTCP+24],16) 
        thl = 4*int(trame[debutTCP+24],16) #le reste est reserved
        flags = (bin(int(trame[debutTCP+25:debutTCP+28],16)))[2:].zfill(6)
        win=int(trame[debutTCP+28:debutTCP+32],16)
        
        msg =""
        finTCP=debutTCP+thl*2
        i=finTCP
        while (i<len(trame)):
            #parfois il y a quelques valeurs hex apres l'entete TCP mais il n'y a pas de protocole HTTP dedans.
            #On le test ici et s'il n'y a pas de HTTP in ignore le reste. (Honestly speaking : On ignore les hex qui n'ont pas de sens.)
            try:
                msg+=bytes.fromhex(trame[i:i+2]).decode('utf-8')
                i+=2
            except Exception:
                break
                #sys.exc_clear()
                
        tcp = TCP(psrc,pdst,seq,ack,thl,flags,win,msg)
        ip.tcp=tcp
        trm = Trame(e)

        return trm
    except (ValueError,IndexError) :
        print("La trame est incomplete. Le programme ignorera cette trame et continuera.")

#creation du fichier text pour la sortie
def createFile(filename):
    rawTrames = []
    #on sauvegarde les trames en str
    rawTrames = readFile(filename)
    if len(rawTrames)==0:
        print("Aucune trame capturée. Fin du programme.")
        sys.exit()
    trames = []
    
    #on transforme strtrame -> Trame
    for t in rawTrames:
        trame = tramReader(t)
        if trame:
            trames.append(tramReader(t))
        #continuer s'il y a une trame vide
        else:
            continue

    flux = Flux(trames)

    #en cas ou le programme est execute dans un autre repertoire ou bien resultats n'existe pas, on le cree
    if not os.path.isdir("resultats"):
        os.makedirs("resultats")

    #fichier resultant = resultats/RESULTAT+nom_du_fichier_test.txt 
    #il sera enregistre dans la repertoire resultats
    if ('/' in filename):
        fileRes="resultats/RESULTAT_"+str.split(filename,'/')[-1] #[:5]
    else :
        fileRes="resultats/RESULTAT_"+filename

    try : 
        file = open(fileRes,"w")
    except OSError:
        print("Probleme au cours de la creation du fichier resultant. Fin du programme.")
        sys.exit()
    with file :
        file.write(flux.writeSortie())
        file.close()
    return fileRes


###################################
############## MAIN ###############
###################################

#Recuperation de nom de fichier qu'on veut tester -> creation du fichier sorti.

print("\n\n Vous avez execute la version BETA du code original. Si vous n'avez pas de probleme concernant Tkinter, executez visualisateur.py pour lancer l'interface graphique du visualisateur. \n Entrez le chemin/le nom du fichier text :\n")
filename = input()
createFile(filename)


