#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Rodrigo Mansilha
# Universidade Federal do Pampa (Unipampa)
# Programa de Pós-Graduação em Eng. de Software (PPGES)
# Bacharelado em: Ciência da Camputação, Eng. de Software, Eng. de Telecomunicações

# Algoritmos



from cProfile import label


try:
	import sys
	import os
	import argparse
	import logging
	import subprocess
	import shlex
	import logging
	from abc import ABC, abstractmethod

	from scipy.special import factorial
	import math
	import numpy as np
	import matplotlib.pyplot as plt
	import scipy.optimize as opt
	import matplotlib.colors as colors
	import matplotlib.cm as cmx


except ImportError as error:
	print(error)
	print()
	print("1. (optional) Setup a virtual environment: ")
	print("  python3 -m venv ~/Python3env/algoritmos ")
	print("  source ~/Python3env/algoritmos/bin/activate ")
	print()
	print("2. Install requirements:")
	print("  pip3 install --upgrade pip")
	print("  pip3 install -r requirements.txt ")
	print()
	sys.exit(-1)

DEFAULT_SEED = None
DEFAULT_N_START = 1
DEFAULT_N_STOP = 10
DEFAULT_N_STEP = 1
DEFAULT_N_MAX  = None
DEFAULT_TRIALS = 3
DEFAULT_OUTPUT = None #"alg_lab.png"
DEFAULT_ALGORITMOS = None # executa todos
DEFAULT_MODELOS = None

DEFAULT_LOG_LEVEL = logging.INFO
TIME_FORMAT = '%Y-%m-%d,%H:%M:%S'

# Lista completa de mapas de cores
# https://matplotlib.org/examples/color/colormaps_reference.html
mapa_cor = plt.get_cmap('tab20')  # carrega tabela de cores conforme dicionário
mapeamento_normalizado = colors.Normalize(vmin=0, vmax=19)  # mapeamento em 20 cores
mapa_escalar = cmx.ScalarMappable(norm=mapeamento_normalizado, cmap=mapa_cor)  # lista de cores final

formatos = ['_', '.', 'v', 'o', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h']

# https://matplotlib.org/3.3.2/api/_as_gen/matplotlib.pyplot.plot.html
# '.'	point marker
# ','	pixel marker
# 'o'	circle marker
# 'v'	triangle_down marker
# '^'	triangle_up marker
# '<'	triangle_left marker
# '>'	triangle_right marker
# '1'	tri_down marker
# '2'	tri_up marker
# '3'	tri_left marker
# '4'	tri_right marker
# 's'	square marker
# 'p'	pentagon marker
# '*'	star marker
# 'h'	hexagon1 marker
# 'H'	hexagon2 marker
# '+'	plus marker
# 'x'	x marker
# 'D'	diamond marker
# 'd'	thin_diamond marker
# '|'	vline marker
# '_'	hline marker


# https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
linestyle_str = [
     ('solid', 'solid'),      # Same as (0, ()) or '-'
     ('dotted', 'dotted'),    # Same as (0, (1, 1)) or '.'
     ('dashed', 'dashed'),    # Same as '--'
     ('dashdot', 'dashdot')]  # Same as '-.'

linestyle_tuple = [
     ('loosely dotted',        (0, (1, 10))),
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('loosely dashed',        (0, (5, 10))),
     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]

def funcao_fatorial(n, cpu):
	'''
	Aproximação fatorial
	:param n: tamanho da instância
	:param cpu: fator de conversão para tempo de CPU
	:return: aproximação
	'''
	return (factorial(n) * cpu)


def funcao_quadratica(n, cpu):
	'''
	Aproximação quadrática
	:param n: tamanho da instância
	:param cpu: fator de conversão para tempo de CPU
	:return: aproximação
	'''
	return (n * n * cpu)


def funcao_linear(n, cpu):
	'''
	Aproximação linear
	:param n: tamanho da instância
	:param cpu: fator de conversão para tempo de CPU
	:return: aproximação
	'''
	return (n * cpu)

def funcao_exponencial(n,cpu):
    return (2**n)*cpu



def imprime_config(args):
	'''
	Mostra os argumentos recebidos e as configurações processadas
	:args: parser.parse_args
	'''
	logging.info("Argumentos:\n\t{0}\n".format(" ".join([x for x in sys.argv])))
	logging.info("Configurações:")
	for k, v in sorted(vars(args).items()):
		logging.info("\t{0}: {1}".format(k, v))
	logging.info("")


class Experimento(ABC):
	computador = ""

	@abstractmethod
	def __init__(self, args):
		self.id = "letraid"
		self.args = args
		self.script = "abc.py"
		self.output = "out.txt"
		self.tamanhos = []
		self.medias = []
		self.desvios = []
		self.aproximados = []
		self.tamanhos_aproximados = []

		indice_cor = 0
		#configurações de plotagem
		self.medicao_legenda = "medicao_legenda"
		self.medicao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+0)
		self.medicao_formato = formatos[1]

		self.aproximacao_legenda = "aproximacao_legenda"
		self.aproximacao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+1)

		self.multiplo = 1

	@abstractmethod
	def g(self, n, c):
		pass

	def executa_experimentos(self):
		# cria string de comando
		comando_str = "python {}".format(self.script)
		comando_str += " --out {}".format(self.output)
		comando_str += " --nstart {}".format(self.args.nstart * self.multiplo)
		comando_str += " --nstop {}".format(self.args.nstop * self.multiplo)
		comando_str += " --nstep {}".format(self.args.nstep * self.multiplo)
		comando_str += " --trials {}".format(self.args.trials)
		if self.args.seed is not None:
			comando_str += " --seed {}".format(self.args.seed)

		print("Comando: {}".format(comando_str))
		# transforma em array por questões de segurança -> https://docs.python.org/3/library/shlex.html
		comando_array = shlex.split(comando_str)

		# executa comando em subprocesso
		subprocess.run(comando_array, check=True)

	def carrega_resultados(self):
		'''
		Carrega dados do arquivo de saída para a memória principal
		'''
		f = open(self.output, "r")

		for l in f:
			if l[0] != "#":
				self.tamanhos.append(int(l.split(" ")[0]))
				self.medias.append(float(l.split(" ")[1]))
				self.desvios.append(float(l.split(" ")[2]))
			if l[0] == "#" and l[1] == "#" and Experimento.computador == "":
				Experimento.computador = l.replace('#',"")
		f.close()

	def imprime_dados(self):
		# mostra dados
		print("Tamanho\tMedia\t\tDesvio\t\tAproximado")
		for i in range(len(self.tamanhos)):
			print("%03d\t%02f\t%02f\t%02f" % (self.tamanhos[i], self.medias[i], self.desvios[i], self.aproximados[i]))
		print("")

	@abstractmethod
	def executa_aproximacao(self):
		pass
	
	def plota_aproximacao(self):
		plt.plot(self.tamanhos_aproximados, self.aproximados, label=self.aproximacao_legenda, color=self.aproximacao_cor_rgb)

	def plota_medicao(self):
		if self.args.aproximacao:
			plt.errorbar(x=self.tamanhos, y=self.medias, yerr=self.desvios, fmt=self.medicao_formato,
					 label=self.medicao_legenda, color=self.medicao_cor_rgb, linewidth=2)
		else:
			plt.plot(self.tamanhos, self.medias, label=self.medicao_legenda, color=self.medicao_cor_rgb, linewidth=2)

	def plota_gn(self, constante, legenda, cor, estilo_linha):
		valores = [self.g(n, constante) for n in self.tamanhos_aproximados]
		logging.debug("valores: {}".format(valores))
		plt.plot(self.tamanhos_aproximados, valores, linestyle=estilo_linha, label=legenda, color=cor)


class FibonacciDinamic(Experimento):

	def __init__(self, args):
		super().__init__(args)
		self.id = "fd"
		self.script = "fibonacci_dinamic.py"
		self.output = "fibonacci_dinamic.txt"

		indice_cor = 1

		# configurações de plotagem
		self.medicao_legenda = "fibonacci dinâmico medido"
		self.medicao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor)
		self.medicao_formato = formatos[indice_cor]

		self.aproximacao_legenda = "fibonacci dinâmico aproximado"
		self.aproximacao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+1)

		self.multiplo = 1
		self.tamanhos_aproximados = range(self.args.nmax * self.multiplo+1)

	def executa_aproximacao(self):
		# realiza aproximação
		parametros, pcov = opt.curve_fit(funcao_linear, xdata=self.tamanhos, ydata=self.medias)
		self.aproximados = [funcao_linear(x, *parametros) for x in self.tamanhos_aproximados ]
		print("aproximados:           {}".format(self.aproximados))
		print("parametros_otimizados: {}".format(parametros))
		print("pcov:                  {}".format(pcov))

	def g(self, n, c):
		return n*c

class FibonacciRecursive(Experimento):

	def __init__(self, args):
		super().__init__(args)
		self.id = "fr"
		self.script = "fibonacci_recursive.py"
		self.output = "fibonacci_recursive.txt"

		indice_cor = 2

		# configurações de plotagem
		self.medicao_legenda = "fibonacci recursivo medido"
		self.medicao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor)
		self.medicao_formato = formatos[indice_cor]

		self.aproximacao_legenda = "fibonacci recursivo aproximado"
		self.aproximacao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+1)

		self.multiplo = 1
		self.tamanhos_aproximados = range(self.args.nmax * self.multiplo+1)

	def executa_aproximacao(self):
		# realiza aproximação
		parametros, pcov = opt.curve_fit(funcao_exponencial, xdata=self.tamanhos, ydata=self.medias)
		self.aproximados = [funcao_exponencial(x, *parametros) for x in self.tamanhos_aproximados ]
		print("aproximados:           {}".format(self.aproximados))
		print("parametros_otimizados: {}".format(parametros))
		print("pcov:                  {}".format(pcov))

	def g(self, n, c):
		return (2**n)*c

class FibonacciIterative(Experimento):

	def __init__(self, args):
		super().__init__(args)
		self.id = "fi"
		self.script = "fibonacci_iterative.py"
		self.output = "fibonacci_iterative.txt"

		indice_cor = 3

		# configurações de plotagem
		self.medicao_legenda = "fibonacci iterativo medido"
		self.medicao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor)
		self.medicao_formato = formatos[indice_cor]

		self.aproximacao_legenda = "fibonacci iterativo aproximado"
		self.aproximacao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+1)

		self.multiplo = 1
		self.tamanhos_aproximados = range(self.args.nmax * self.multiplo+1)

	def executa_aproximacao(self):
		# realiza aproximação
		parametros, pcov = opt.curve_fit(funcao_linear, xdata=self.tamanhos, ydata=self.medias)
		self.aproximados = [funcao_linear(x, *parametros) for x in self.tamanhos_aproximados ]
		print("aproximados:           {}".format(self.aproximados))
		print("parametros_otimizados: {}".format(parametros))
		print("pcov:                  {}".format(pcov))

	def g(self, n, c):
		return n*c

class FibonacciMath(Experimento):

	def __init__(self, args):
		super().__init__(args)
		self.id = "fm"
		self.script = "fibonacci_math.py"
		self.output = "fibonacci_math.txt"

		indice_cor = 4

		# configurações de plotagem
		self.medicao_legenda = "fibonacci matemático medido"
		self.medicao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor)
		self.medicao_formato = formatos[indice_cor]

		self.aproximacao_legenda = "fibonacci matemático aproximado"
		self.aproximacao_cor_rgb = mapa_escalar.to_rgba(2*indice_cor+1)

		self.multiplo = 1
		self.tamanhos_aproximados = range(self.args.nmax * self.multiplo+1)

	def executa_aproximacao(self):
		# realiza aproximação
		parametros, pcov = opt.curve_fit(funcao_linear, xdata=self.tamanhos, ydata=self.medias)
		self.aproximados = [funcao_linear(x, *parametros) for x in self.tamanhos_aproximados ]
		print("aproximados:           {}".format(self.aproximados))
		print("parametros_otimizados: {}".format(parametros))
		print("pcov:                  {}".format(pcov))

	def g(self, n, c):
		return c


def main():
	'''
	Programa principal
	:return:
	'''
	# Definição de argumentos
	parser = argparse.ArgumentParser(description='Trabalho Fibonacci')

	help_msg = "semente aleatória"
	parser.add_argument("--seed", "-s", help=help_msg, default=DEFAULT_SEED, type=int)

	help_msg = "aproximação.          Padrão:{}".format(DEFAULT_N_STOP)
	parser.add_argument("--aproximacao", "-apr", help=help_msg, default=False, type=bool)

	help_msg = "n stop.          Padrão:{}".format(DEFAULT_N_STOP)
	parser.add_argument("--nstop", "-n", help=help_msg, default=DEFAULT_N_STOP, type=int)

	help_msg = "n mínimo.          Padrão:{}".format(DEFAULT_N_START)
	parser.add_argument("--nstart", "-a", help=help_msg, default=DEFAULT_N_START, type=int)

	help_msg = "n passo.           Padrão:{}".format(DEFAULT_N_STEP)
	parser.add_argument("--nstep", "-e", help=help_msg, default=DEFAULT_N_STEP, type=int)

	help_msg = "n máximo.          Padrão:{}".format(DEFAULT_N_MAX)
	parser.add_argument("--nmax", "-m", help=help_msg, default=DEFAULT_N_MAX, type=int)

	help_msg = "tentativas.        Padrão:{}".format(DEFAULT_TRIALS)
	parser.add_argument("--trials", "-t", help=help_msg, default=DEFAULT_TRIALS, type=int)

	help_msg = "figura (extensão .png ou .pdf) ou nenhum para apresentar na tela.  Padrão:{}".format(DEFAULT_OUTPUT)
	parser.add_argument("--out", "-o", help=help_msg, default=DEFAULT_OUTPUT, type=str)

	help_msg = "algoritmos (fd=fibonacci dinâmico), (fr=fibonacci recursivo), (fi=fibonacci iterativo), (fm=fibonacci matemático) ou nenhum para executar todos.  Padrão:{}".format(DEFAULT_ALGORITMOS)
	parser.add_argument("--algoritmos", "-l", help=help_msg, default=DEFAULT_ALGORITMOS, type=str)

	help_msg = "verbosity logging level (INFO=%d DEBUG=%d)" % (logging.INFO, logging.DEBUG)
	parser.add_argument("--verbosity", "-v", help=help_msg, default=DEFAULT_LOG_LEVEL, type=int)

	#action='store_true'
	parser.add_argument("--skip", "-k", default=False, help="Pula execução.", action='store_true')

	# Lê argumentos da linha de comando
	args = parser.parse_args()
	if args.nmax is None:
		args.nmax = args.nstop

	# configura o mecanismo de logging
	if args.verbosity == logging.DEBUG:
		# mostra mais detalhes
		logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
							datefmt=TIME_FORMAT, level=args.verbosity)

	else:
		logging.basicConfig(format='%(message)s',
							datefmt=TIME_FORMAT, level=args.verbosity)

	# imprime configurações para fins de log
	imprime_config(args)

	# lista de experimentos disponíveis TspNaive(args),
	experimentos = [FibonacciDinamic(args), FibonacciRecursive(args), FibonacciIterative(args), FibonacciMath(args)]

	for e in experimentos:
		if args.algoritmos is None or e.id in args.algoritmos:
			if not args.skip:
				e.executa_experimentos()
			e.carrega_resultados()
			e.executa_aproximacao()
			e.imprime_dados()
			e.plota_medicao()

			if args.aproximacao:
				e.plota_aproximacao()

	# configurações gerais
	plt.legend()
	plt.title("Fibonacci - Impacto de n \n {}".format(Experimento.computador))
	plt.xlabel("Tamanho da instância (n)")
	plt.ylabel("Tempo em Segundos")
	if args.out is None:
		# mostra
		plt.show()
	else:
		# salva em png
		plt.savefig(args.out, dpi=300)


if __name__ == '__main__':
	sys.exit(main())
