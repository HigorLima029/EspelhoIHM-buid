# -*- coding: utf-8 -*-
# Espelho IHM Chen Hsong - programa com interface (para virar .exe).
# Pede IP e senha, testa a conexao, mostra a tela e permite operar (painel touch: clique = toque).
# F12 liga/desliga o controle. Mantenha o Caps Lock desligado.

import socket, struct, time, threading
import tkinter as tk

IP = None
SENHA = ""

# ------------------- DES (so para a autenticacao VNC) -------------------
IP_TAB=[58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,
62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,
61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
FP_TAB=[40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]
E_TAB=[32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,
16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]
P_TAB=[16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,
2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
PC1=[57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,
59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,
31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4]
PC2=[14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,
26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,
51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]
SHIFT=[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
SBOX=[
[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,
4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13],
[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10,3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5,
0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15,13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9],
[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8,13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1,
13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7,1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12],
[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15,13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9,
10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4,3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14],
[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9,14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6,
4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14,11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11,10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8,
9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6,4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13],
[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1,13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6,
1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2,6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12],
[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7,1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2,
7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8,2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]

def _perm(bits,tab): return [bits[i-1] for i in tab]
def _b2bits(b):
    out=[]
    for x in b:
        for i in range(7,-1,-1): out.append((x>>i)&1)
    return out
def _bits2b(bits):
    out=bytearray()
    for i in range(0,len(bits),8):
        v=0
        for j in range(8): v=(v<<1)|bits[i+j]
        out.append(v)
    return bytes(out)
def _keys(key8):
    k=_perm(_b2bits(key8),PC1); c=k[:28]; d=k[28:]; ks=[]
    for s in SHIFT:
        c=c[s:]+c[:s]; d=d[s:]+d[:s]; ks.append(_perm(c+d,PC2))
    return ks
def _f(r,k):
    x=[a^b for a,b in zip(_perm(r,E_TAB),k)]; out=[]
    for i in range(8):
        blk=x[i*6:i*6+6]
        row=(blk[0]<<1)|blk[5]
        col=(blk[1]<<3)|(blk[2]<<2)|(blk[3]<<1)|blk[4]
        val=SBOX[i][row*16+col]
        for j in range(3,-1,-1): out.append((val>>j)&1)
    return _perm(out,P_TAB)
def des_block(key8,block8):
    ks=_keys(key8); bits=_perm(_b2bits(block8),IP_TAB); l=bits[:32]; r=bits[32:]
    for i in range(16):
        l,r=r,[a^b for a,b in zip(l,_f(r,ks[i]))]
    return _bits2b(_perm(r+l,FP_TAB))
def espelha_bits(b):
    r=0
    for i in range(8): r=(r<<1)|((b>>i)&1)
    return r
def vncauth(senha,desafio):
    chave=(senha.encode("latin-1","ignore")[:8]+b"\x00"*8)[:8]
    chave=bytes(espelha_bits(x) for x in chave)
    return des_block(chave,desafio[:8])+des_block(chave,desafio[8:16])

# ------------------- cliente RFB 3.3 -------------------
lock=threading.Lock()
st={"dirty":False,"frames":0,"msg":"conectando","sock":None}
ctl={"on":False,"btn":0}
W=0; H=0
fb=bytearray()

def rd(s,n):
    d=b""
    while len(d)<n:
        p=s.recv(n-len(d))
        if not p: raise OSError("conexao fechada")
        d+=p
    return d

def conectar():
    global W,H,fb
    s=socket.create_connection(IP,timeout=10)
    rd(s,12)                         # versao do servidor
    s.send(b"RFB 003.003\n")         # nossa versao
    sec=struct.unpack(">I",rd(s,4))[0]
    if sec==0:
        raise OSError("servidor recusou a conexao")
    if sec==2:                       # VncAuth: desafio/resposta
        desafio=rd(s,16)
        s.send(vncauth(SENHA,desafio))
        if struct.unpack(">I",rd(s,4))[0]!=0:
            raise SystemExit("senha VNC recusada")
    elif sec!=1:                     # 1 = sem autenticacao
        raise OSError("tipo de seguranca nao suportado: %d"%sec)
    s.send(b"\x01")                  # ClientInit (compartilhado)
    h=rd(s,24); w,hh=struct.unpack(">HH",h[:4]); rd(s,struct.unpack(">I",h[20:24])[0])
    W=w; H=hh; fb=bytearray(W*H*3)
    # formato de pixel fixo 32bpp BGRX
    s.send(struct.pack(">B3xBBBBHHHBBB3x",0,32,24,0,1,255,255,255,16,8,0))
    s.send(struct.pack(">BxHi",2,1,0))          # so codificacao Raw
    return s,w,hh

def pedir(s,incremental):
    s.send(struct.pack(">BBHHHH",3,incremental,0,0,W,H))

def pintar(x,y,w,h,dados):
    for linha in range(h):
        src=linha*w*4
        trecho=dados[src:src+w*4]
        rgb=bytearray(w*3)
        rgb[0::3]=trecho[2::4]
        rgb[1::3]=trecho[1::4]
        rgb[2::3]=trecho[0::4]
        dst=((y+linha)*W+x)*3
        fb[dst:dst+w*3]=rgb

def ler(s):
    tipo=rd(s,1)[0]
    if tipo==0:                                  # FramebufferUpdate
        rd(s,1)
        n=struct.unpack(">H",rd(s,2))[0]
        for _ in range(n):
            cab=rd(s,12)
            x,y,w,h=struct.unpack(">HHHH",cab[:8])
            enc=struct.unpack(">i",cab[8:12])[0]
            if enc==0:
                dados=rd(s,w*h*4)
                with lock:
                    pintar(x,y,w,h,dados)
            else:
                raise OSError("codificacao inesperada: %d"%enc)
        st["frames"]+=1
        st["dirty"]=True
        pedir(s,1)
    elif tipo==2:                                # Bell
        pass
    elif tipo==3:                                # ServerCutText
        rd(s,3); ln=struct.unpack(">I",rd(s,4))[0]; rd(s,ln)
    elif tipo==1:                                # SetColourMapEntries
        rd(s,3); nn=struct.unpack(">H",rd(s,2))[0]; rd(s,nn*6)

def loop():
    while True:
        try:
            s,w,hh=conectar()
            st["sock"]=s
            st["msg"]="%dx%d"%(w,hh)
            pedir(s,0)
            while True:
                ler(s)
        except SystemExit as e:
            st["msg"]=str(e)
            st["sock"]=None
            time.sleep(3)
        except Exception as e:
            st["msg"]="sem conexao (%s)"%e
            st["sock"]=None
            time.sleep(3)


# ------------------- INTERFACE: espelho + controle + legenda -------------------
# Mapa oficial do fabricante: tecla do PC -> funcao da maquina.
LEGENDA = [
 ("MOVIMENTOS (cuidado)",""),
 ("1","Abrir molde (Clamp Open)"),
 ("2","Fechar molde (Clamp Close)"),
 ("4","Macho entra (Core In)"),
 ("5","Macho sai (Core Out)"),
 ("9","Injecao (Injection)"),
 ("0","Plastificacao (Plast.)"),
 ("-","Descompressao (Decomp.)"),
 ("Q","Extrator recua (Eje.Bwd)"),
 ("W","Extrator avanca (Eje.Fwd)"),
 ("R","Altura molde - (MoldH.Dec)"),
 ("T","Altura molde + (MoldH.Inc)"),
 ("U","Sopro de ar (Air Blow)"),
 ("O","Unid.inj. avanca (InjU.Fwd)"),
 ("P","Unid.inj. recua (InjU.Bwd)"),
 ("A","Porta seg. abre (SafeGateOpen)"),
 ("S","Porta seg. fecha (SafeGateClose)"),
 ("F","Comando manual (Cmd Man.)"),
 ("H","Bico avanca (Nozzle Pos)"),
 ("J","Bico recua (Nozzle Neg)"),
 ("L","Rotacao unid. + (IU.R Pos.)"),
 (";","Rotacao unid. - (IU.R Neg)"),
 ("BARRA / TELAS",""),
 ("Z","Barra icone 22 (motor)"),
 ("X","Barra icone 23 (temperatura)"),
 ("C","Barra icone 24"),
 ("V","Barra icone 25"),
 ("B","Barra icone 26"),
 ("N","Barra icone 27"),
 ("M","Barra icone 28"),
 (",","Barra icone 29"),
 (".","Barra icone 30 (chave inglesa/ajustes)"),
]

sl=threading.Lock()

# ------------------- teste de conexao -------------------
def teste_conexao(ip, porta=5900, timeout=4):
    try:
        s = socket.create_connection((ip, porta), timeout=timeout)
        s.close()
        return True, ""
    except Exception as e:
        return False, str(e)

# ------------------- janela do espelho -------------------
def iniciar_espelho(dialog_frame):
    dialog_frame.destroy()
    root.title("IHM Chen Hsong - conectando...")

    esc = [1]      # fator de reducao da imagem (1 = real, 2 = metade...)
    fit = [False]  # ja encaixou na tela automaticamente?

    bar = tk.Frame(root, bg="#222")
    bar.pack(fill="x")
    aviso = tk.Label(bar, text="Conectando...", fg="#ddd", bg="#222", anchor="w")
    aviso.pack(side="left", padx=6)
    def _repaint(): st["dirty"] = True
    def zoom_mais():
        if esc[0] > 1: esc[0] -= 1; _repaint()
    def zoom_menos():
        esc[0] += 1; _repaint()
    def zoom_fit():
        fit[0] = False; _repaint()
    tk.Button(bar, text="Encaixar", command=zoom_fit).pack(side="right", padx=2, pady=2)
    tk.Button(bar, text="+", width=3, command=zoom_mais).pack(side="right", padx=2, pady=2)
    tk.Button(bar, text="-", width=3, command=zoom_menos).pack(side="right", padx=2, pady=2)

    area = tk.Frame(root)
    area.pack(fill="both", expand=True)
    vs = tk.Scrollbar(area, orient="vertical")
    hs = tk.Scrollbar(area, orient="horizontal")
    cv = tk.Canvas(area, bg="#000", highlightthickness=0,
                   yscrollcommand=vs.set, xscrollcommand=hs.set)
    vs.config(command=cv.yview); hs.config(command=cv.xview)
    vs.pack(side="right", fill="y")
    hs.pack(side="bottom", fill="x")
    cv.pack(side="left", fill="both", expand=True)
    img_id = cv.create_image(0, 0, anchor="nw")
    vp = [False]   # viewport ja dimensionado?
    def _wheel(e):
        d = 0
        if getattr(e, "num", 0) == 4 or getattr(e, "delta", 0) > 0: d = -1
        elif getattr(e, "num", 0) == 5 or getattr(e, "delta", 0) < 0: d = 1
        if e.state & 0x1: cv.xview_scroll(d, "units")   # Shift = horizontal
        else: cv.yview_scroll(d, "units")
    cv.bind("<MouseWheel>", _wheel); cv.bind("<Button-4>", _wheel); cv.bind("<Button-5>", _wheel)

    threading.Thread(target=loop, daemon=True).start()

    t0 = [time.time(), 0]
    def refresh():
        if st["dirty"] and W > 0 and H > 0:
            st["dirty"] = False
            if not fit[0]:
                uh = max(200, root.winfo_screenheight() - 140)
                uw = max(200, root.winfo_screenwidth() - 60)
                esc[0] = max(1, (W + uw - 1) // uw, (H + uh - 1) // uh)
                fit[0] = True
            with lock:
                data = bytes(fb)
            hdr = ("P6\n%d %d\n255\n" % (W, H)).encode()
            img = tk.PhotoImage(data=hdr + data, format="PPM")
            if esc[0] > 1:
                img = img.subsample(esc[0], esc[0])
            cv.itemconfig(img_id, image=img); cv.image = img
            cv.config(scrollregion=(0, 0, img.width(), img.height()))
            if not vp[0]:
                vw = min(img.width(), max(200, root.winfo_screenwidth() - 80))
                vh = min(img.height(), max(200, root.winfo_screenheight() - 170))
                cv.config(width=vw, height=vh)
                vp[0] = True
        now = time.time()
        if now - t0[0] >= 1.5:
            t0[0] = now; t0[1] = st["frames"]
            estado = "CONTROLE LIGADO (F12 desliga)" if ctl["on"] else "so visualizacao (F12 liga)"
            root.title("IHM Chen Hsong | %s | zoom 1/%d | %s" % (st["msg"], esc[0], estado))
            if st["frames"] == 0:
                aviso.config(text="%s  -  se pedir senha e recusar, confira a senha de operacao." % st["msg"])
            else:
                aviso.config(text="F12 %s  |  clique opera (toque)  |  use + / - / Encaixar para o zoom" %
                             ("CONTROLE LIGADO" if ctl["on"] else "desligado"))
        root.after(100, refresh)
    refresh()

    sl = threading.Lock()
    def enviar(b):
        s = st.get("sock")
        if s and ctl["on"]:
            try:
                with sl: s.sendall(b)
            except OSError: pass
    def ptr(e, mask):
        x = max(0, min(W - 1, int(cv.canvasx(e.x)) * esc[0]))
        y = max(0, min(H - 1, int(cv.canvasy(e.y)) * esc[0]))
        enviar(struct.pack(">BBHH", 5, mask, x, y))
    def mdown(e): ctl["btn"] = 1; ptr(e, 1)
    def mmove(e): ptr(e, ctl["btn"])
    def mup(e): ctl["btn"] = 0; ptr(e, 0)
    cv.bind("<ButtonPress-1>", mdown); cv.bind("<B1-Motion>", mmove); cv.bind("<ButtonRelease-1>", mup)
    KS = {"Return":0xff0d,"KP_Enter":0xff8d,"BackSpace":0xff08,"Tab":0xff09,"Escape":0xff1b,"Delete":0xffff,
          "Left":0xff51,"Up":0xff52,"Right":0xff53,"Down":0xff54,"Home":0xff50,"End":0xff57,
          "Prior":0xff55,"Next":0xff56,"Shift_L":0xffe1,"Shift_R":0xffe2}
    for i in range(12): KS["F%d" % (i+1)] = 0xffbe + i
    def ksym(e):
        if e.keysym in KS: return KS[e.keysym]
        if e.char and len(e.char) == 1 and ord(e.char) >= 32: return ord(e.char)
        return None
    def kdown(e):
        k = ksym(e)
        if k: enviar(struct.pack(">BBxxI", 4, 1, k))
    def kup(e):
        k = ksym(e)
        if k: enviar(struct.pack(">BBxxI", 4, 0, k))
    def alternar(e=None):
        ctl["on"] = not ctl["on"]
        cv.config(highlightthickness=5 if ctl["on"] else 0, highlightbackground="red")
    root.bind("<KeyPress>", kdown); root.bind("<KeyRelease>", kup); root.bind("<F12>", alternar)

# ------------------- janela inicial (IP + senha) -------------------
root = tk.Tk()
root.title("Espelho IHM Chen Hsong")
root.configure(bg="#f0f0f0")
frm = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
frm.pack()

tk.Label(frm, text="Espelho da IHM (Chen Hsong)", font=("Arial", 14, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=(0,12))
tk.Label(frm, text="IP da maquina:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", pady=4)
ent_ip = tk.Entry(frm, width=22); ent_ip.grid(row=1, column=1, pady=4, padx=6); ent_ip.insert(0, "192.168.137.1")
tk.Label(frm, text="Senha do VNC:", bg="#f0f0f0").grid(row=2, column=0, sticky="e", pady=4)
ent_pw = tk.Entry(frm, width=22, show="*"); ent_pw.grid(row=2, column=1, pady=4, padx=6)
status = tk.Label(frm, text="", bg="#f0f0f0", justify="left", wraplength=320)
status.grid(row=4, column=0, columnspan=2, pady=(10,0))

def do_connect(e=None):
    ip = ent_ip.get().strip(); pw = ent_pw.get()
    if not ip:
        status.config(text="Informe o IP da maquina.", fg="#b00"); return
    btn.config(state="disabled")
    status.config(text="Testando conexao com %s..." % ip, fg="#333")
    def work():
        ok, err = teste_conexao(ip)
        def done():
            if not ok:
                status.config(fg="#b00", text=(
                    "SEM CONEXAO com %s (porta VNC 5900).\n\n"
                    "Confira:\n"
                    " - o cabo de rede ligado na maquina e no PC\n"
                    " - o IP da maquina (confira na tela de rede do painel)\n"
                    " - o PC esta na mesma faixa de IP da maquina\n"
                    " - o VNC esta ligado no painel\n\n(%s)" % (ip, err)))
                btn.config(state="normal")
            else:
                globals()["IP"] = (ip, 5900)
                globals()["SENHA"] = pw
                iniciar_espelho(frm)
        root.after(0, done)
    threading.Thread(target=work, daemon=True).start()

btn = tk.Button(frm, text="Testar e conectar", command=do_connect, bg="#2d6cdf", fg="white", font=("Arial", 11, "bold"))
btn.grid(row=3, column=0, columnspan=2, pady=(12,0), ipadx=8, ipady=2)
root.bind("<Return>", do_connect)
ent_pw.focus()
root.mainloop()
