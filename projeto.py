from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


engine = create_engine('sqlite:///mercado.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    categoria = Column(String)
    preco = Column(Float)
    descricao = Column(Text)
    estoque = Column(Integer)

    def __repr__(self):
        return f'<Produto(nome={self.nome}, preco={self.preco}, estoque={self.estoque})>'


class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    endereco = Column(String)
    email = Column(String, unique=True)
    telefone = Column(String)

    def __repr__(self):
        return f'<Cliente(nome={self.nome}, email={self.email})>'


class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    valor_total = Column(Float)
    status = Column(String)
    cliente = relationship('Cliente', backref='pedidos')
    produtos = relationship('ProdutoPedido', back_populates='pedido')

class ProdutoPedido(Base):
    __tablename__ = 'produtos_pedidos'

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer)
    pedido = relationship('Pedido', back_populates='produtos')
    produto = relationship('Produto')


class Pagamento(Base):
    __tablename__ = 'pagamentos'

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    valor_pago = Column(Float)
    metodo_pagamento = Column(String)
    pedido = relationship('Pedido')

Base.metadata.create_all(engine)

def adicionar_produto(nome, categoria, preco, descricao, estoque):
    produto = Produto(nome=nome, categoria=categoria, preco=preco, descricao=descricao, estoque=estoque)
    session.add(produto)
    session.commit()

def adicionar_cliente(nome, endereco, email, telefone):
    cliente = Cliente(nome=nome, endereco=endereco, email=email, telefone=telefone)
    session.add(cliente)
    session.commit()

def consultar_produtos(filtro=None):
    query = session.query(Produto)
    if filtro:
        query = query.filter(Produto.nome.ilike(f'%{filtro}%'))
    return query.all()

def realizar_pedido(cliente_id, produtos_quantidade):
    cliente = session.query(Cliente).get(cliente_id)
    if not cliente:
        print("Cliente não encontrado.")
        return
    
    pedido = Pedido(cliente=cliente, status='Pendente', valor_total=0)
    for produto_id, quantidade in produtos_quantidade.items():
        produto = session.query(Produto).get(produto_id)
        if produto and produto.estoque >= quantidade:
            produto_pedido = ProdutoPedido(pedido=pedido, produto=produto, quantidade=quantidade)
            pedido.valor_total += produto.preco * quantidade
            produto.estoque -= quantidade
            session.add(produto_pedido)
        else:
            print(f'Produto {produto_id} não disponível ou estoque insuficiente.')

    session.add(pedido)
    session.commit()

def consultar_pedidos(cliente_id):
    return session.query(Pedido).filter_by(cliente_id=cliente_id).all()

def main():
    while True:
        print('\nEscolha uma opção:')
        print('1. Adicionar Produto')
        print('2. Adicionar Cliente')
        print('3. Consultar Produtos')
        print('4. Realizar Pedido')
        print('5. Consultar Pedidos')
        print('6. Sair')

        opcao = input('Opção: ')
        if opcao == '1':
            nome = input('Nome do Produto: ')
            categoria = input('Categoria: ')
            preco = float(input('Preço: '))
            descricao = input('Descrição: ')
            estoque = int(input('Estoque: '))
            adicionar_produto(nome, categoria, preco, descricao, estoque)
        elif opcao == '2':
            nome = input('Nome do Cliente: ')
            endereco = input('Endereço: ')
            email = input('E-mail: ')
            telefone = input('Telefone: ')
            adicionar_cliente(nome, endereco, email, telefone)
        elif opcao == '3':
            filtro = input('Filtrar por nome (deixe vazio para todos): ')
            produtos = consultar_produtos(filtro)
            for produto in produtos:
                print(produto)
        elif opcao == '4':
            cliente_id = int(input('ID do Cliente: '))
            produtos_quantidade = {}
            while True:
                produto_id = int(input('ID do Produto (0 para finalizar): '))
                if produto_id == 0:
                    break
                quantidade = int(input('Quantidade: '))
                produtos_quantidade[produto_id] = quantidade
            realizar_pedido(cliente_id, produtos_quantidade)
        elif opcao == '5':
            cliente_id = int(input('ID do Cliente: '))
            pedidos = consultar_pedidos(cliente_id)
            for pedido in pedidos:
                print(f'Pedido ID: {pedido.id}, Valor Total: {pedido.valor_total}, Status: {pedido.status}')
        elif opcao == '6':
            break
        else:
            print('Opção inválida. Tente novamente.')

if __name__ == "__main__":
    main()
