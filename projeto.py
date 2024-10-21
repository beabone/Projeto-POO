class Produto:
    def _init_ (self, produto, preço, marca, estoque_disponivel):
        self.nome = nome
        self.preco = preço
        self.categoria = marca
        self.estoque_disponivel = estoque_disponivel
    
class Cliente:
    def _init_(self, nome, telefone, historico_de_compras, produto, preço, marca, estoque_disponivel):
        super()._init_(produto, preço, marca, estoque_disponivel)
        self.nome = nome
        self.telefone = telefone
        self.historico_de_compras = []
    
    def adicionar_compra(self, compra):
        self.historico_de_compras.append(compra)
        
    def total_compras (self):
        return sum(compra.calcular_total() for compra in self.historico_de_compras)

class Compra:
    def _init_(self, data_compra, cliente_associado, produtos_comprados, status):
        self.data_compra = data_compra
        self.cliente_associado = cliente_associado
        self.produtos_comprados = produtos_comprados
        self.status = status
    
    def calcular_total(self):
        return sum(produto.preço for produto in self.produtos_comprados)
