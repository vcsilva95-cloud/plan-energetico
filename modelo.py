# -*- coding: utf-8 -*-
lista_uhe = []

usina = {
    "Nome": "UHE CHAVANTES",
    "Vmax": 8795.,
    "Vmin": 5754.,
    "VI": 8000.,
    "Prod": 0.235,
    "Engol": 1628.,
    "Afl": [
        [2156.11, 508.90],   # Jan
        [1838.59, 713.66],   # Fev
        [1674.00, 656.21],   # Mar
        [1153.44, 466.56],   # Abr
        [1218.67, 361.58],   # Mai
        [1464.48, 155.52],   # Jun
        [1098.14, 334.80],   # Jul
        [883.87, 308.02],    # Ago
        [1114.56, 220.32],   # Set
        [1280.28, 334.80],   # Out
        [1101.60, 375.84],   # Nov
        [1406.16, 468.72]    # Dez
    ]
}
lista_uhe.append(usina)


usina = {
    "Nome": "UHE PIRAJU",
    "Vmax": 85.,
    "Vmin": 83.,
    "VI": 84.,
    "Prod": 0.089,
    "Engol": 899.16,
    "Afl": [
        [1379.38, 374.98],   # Jan
        [1270.08, 483.84],   # Fev
        [1178.50, 455.33],   # Mar
        [790.56, 336.96],    # Abr
        [749.95, 267.84],    # Mai
        [972.00, 90.72],     # Jun
        [696.38, 227.66],    # Jul
        [575.86, 214.27],    # Ago
        [686.88, 168.48],    # Set
        [790.13, 241.06],    # Out
        [699.84, 266.98],    # Nov
        [937.44, 308.02]     # Dez
    ]
}
lista_uhe.append(usina)


usina={"Nome":"UTE_Termobahia",
       "Capac": 186.,
       "Custo":424080.,}
lista_ute=[]

lista_ute.append(usina)

usina={"Nome":"UTE_Pecém_II",
       "Capac": 144.,
       "Custo":1764000.,}

lista_ute.append(usina)

d_gerais = {
    "CDef": 5969520,
    "Carga": [
        530.,  # Jan
        508.,  # Fev
        516.,  # Mar
        437.,  # Abr
        420.,  # Mai
        401.,  # Jun
        390.,  # Jul
        411.,  # Ago
        454.,  # Set
        490.,  # Out
        506.,  # Nov
        504.    # Dez
    ],
    "Nr_Disc": 3,
    "Nr_Est": 12,
    "Nr_Cen": 2
}

sistema={"DGer":d_gerais,
         "UHE":lista_uhe,
         "UTE":lista_ute}

from cvxopt.modeling import variable, solvers
from cvxopt.modeling import op

#### FUNCAO DE DESPACHO ####
def pl_unico(sistema,cenario, imprime):

  Num_UHE = len(sistema["UHE"])

  Num_UTE = len(sistema["UTE"])
  vf = []
  vt = []
  vv = []
  for i, iusi in enumerate(sistema["UHE"]):
    vf.append(variable(sistema["DGer"]["Nr_Est"], "Volume Final na Usina"+iusi["Nome"]))
    vt.append(variable(sistema["DGer"]["Nr_Est"], "Volume Turbinado na Usina"+iusi["Nome"]))
    vv.append(variable(sistema["DGer"]["Nr_Est"], "Volume Vertido na Usina"+iusi["Nome"]))

  gt = []
  for i, iusi in enumerate(sistema["UTE"]):
    gt.append(variable(sistema["DGer"]["Nr_Est"], "GeraÃ§Ã£o na Usina TÃ©rmica"+iusi["Nome"]))
  deficit = variable(sistema["DGer"]["Nr_Est"],"Deficit de energia no sistema")



  # ConstruÃ§Ã£o da funÃ§Ã£o objetivo

  fob = 0

  for i_est in range(sistema["DGer"]["Nr_Est"]):
    for i, iusi in enumerate(sistema["UTE"]):
      fob += iusi['Custo']*gt[i][i_est]

    fob += sistema["DGer"]["CDef"]*deficit[i_est]

    for i, iusi in enumerate(sistema["UHE"]):
      fob += 0.01*vv[i][i_est]

  # DefiniÃ§Ã£o das restriÃ§Ãµes

  restricoes = []

  # BalanÃ§o hÃ­drico

  for i, iusi in enumerate(sistema["UHE"]):
    for i_est in range(sistema["DGer"]["Nr_Est"]):
      if i_est == 0:
        restricoes.append(vf[i][i_est] == float(iusi["VI"]) + float(iusi["Afl"][i_est][cenario]) - vt[i][i_est] - vv[i][i_est])
      else:
        restricoes.append(vf[i][i_est] == vf[i][i_est-1] + float(iusi["Afl"][i_est][cenario]) - vt[i][i_est] - vv[i][i_est])

  # Atendimento Ã  Demanda

  for i_est in range(sistema["DGer"]["Nr_Est"]):
    AD = 0
    for i, usi in enumerate(sistema["UHE"]):
      AD += usi["Prod"]*vt[i][i_est]
    for i, usi in enumerate(sistema["UTE"]):
      AD += gt[i][i_est]
    AD += deficit[i_est]
    restricoes.append(AD == sistema["DGer"]["Carga"][i_est])

  # RestriÃ§Ãµes de CanalizaÃ§Ã£o

  for i, iusi in enumerate(sistema["UHE"]):
    for i_est in range(sistema["DGer"]["Nr_Est"]):
        restricoes.append(vf[i][i_est] >= iusi["Vmin"])
        restricoes.append(vf[i][i_est] <= iusi["Vmax"])
        restricoes.append(vt[i][i_est] >= 0)
        restricoes.append(vt[i][i_est] <= iusi["Engol"])
        restricoes.append(vv[i][i_est] >= 0)

  for i, iusi in enumerate(sistema["UTE"]):
    for i_est in range(sistema["DGer"]["Nr_Est"]):
      restricoes.append(gt[i][i_est] >= 0)
      restricoes.append(gt[i][i_est] <= iusi["Capac"])

  for i_est in range(sistema["DGer"]["Nr_Est"]):
    restricoes.append(deficit[i_est] >= 0)

#OTIMIZAÃ‡ÃƒO
  problema = op(fob,restricoes)
  problema.solve('dense','glpk')


  lista_UHE = []
  for i, iusi in enumerate(sistema["UHE"]):
    pula=i*sistema["DGer"]["Nr_Est"]
    cma = []
    volf = []
    volt = []
    volv = []

    # GeraÃ§Ã£o hidrÃ¡ulica de cada estÃ¡gio
    gerhid = []
    
    for i_est in range(sistema["DGer"]["Nr_Est"]):

      cma.append(restricoes[pula + i_est].multiplier.value[0])

      volf.append(vf[i][i_est].value()[0])

      volt.append(vt[i][i_est].value()[0])

      volv.append(vv[i][i_est].value()[0])

      # GeraÃ§Ã£o hidrÃ¡ulica = produtividade Ã— volume turbinado
      gerhid.append(iusi["Prod"] * vt[i][i_est].value()[0])
        
    elemento = {
      "vf": volf,
      "vt": volt,
      "vv": volv,
      "gh": gerhid,
      "cma": cma
      }
    lista_UHE.append(elemento)

  lista_UTE = []

  for i, iusi in enumerate(sistema["UTE"]):
    gerter = []

    for i_est in range(sistema["DGer"]["Nr_Est"]):
      gerter.append(
          gt[i][i_est].value()[0]
      )

    resultado_ute = {
        "gt": gerter
    }

    lista_UTE.append(resultado_ute)

    
  pula = Num_UHE*sistema["DGer"]["Nr_Est"]
  cmo = []
  for i_est in range(sistema["DGer"]["Nr_Est"]):
    cmo.append(restricoes[pula+i_est].multiplier.value[0])

  Dger = {"CustoTotal": fob.value()[0],
      "CMO": cmo}

  lista_deficit = []

  for i_est in range(sistema["DGer"]["Nr_Est"]):
    lista_deficit.append(deficit[i_est].value()[0])
    
  resultado={
      "DGer": Dger,
      "UHE": lista_UHE,
      "UTE": lista_UTE,
      "Deficit": lista_deficit}

## IMPRIME ##

  if imprime:
     print("Custo Total:",fob.value())

     print("Volume Final por UHE em cada estÃ¡gio em hÂ³ ")
     for i, usi in enumerate(sistema["UHE"]):
        print(vf[i])
        print(vt[i])
        print(vv[i])

     print("GeraÃ§Ã£o por UTE em cada EstÃ¡gio em MWmÃ©d ")
     for i, usi in enumerate(sistema["UTE"]):
       print(gt[i])

     print("DÃ©ficit de energia em cada estÃ¡gio em MWmed ")
     print(deficit)
     print("------------------x------------------")
  return(resultado)
