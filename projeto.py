class Produto:
    def _init_ (self, produto, preço, marca, estoque_disponivel):
        self.produtos = []

    def adicionar_produto(self, produto):
        self.produtos.append (produto)
        
    
class Cliente:
    def _init_(self, nome, telefone, historico_de_compras, produto, preço, marca, estoque_disponivel):
        super()._init_(produto, preço, marca, estoque_disponivel)
        self.clientes = []

    def adicionar_cliente(self, cliente):
        self.clientes.append (cliente)
        
    def total_compra(self,):

class Compra:
    def _init_(self, data_compra, cliente_associado, produtos_comprados, status):