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
    try:
        produto = Produto(nome=nome, categoria=categoria, preco=preco, descricao=descricao, estoque=estoque)
        session.add(produto)
        session.commit()
        print(f'Produto {nome} adicionado com sucesso.')
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar produto: {e}")

def adicionar_cliente(nome, endereco, email, telefone):
    try:
        cliente = Cliente(nome=nome, endereco=endereco, email=email, telefone=telefone)
        session.add(cliente)
        session.commit()
        print(f'Cliente {nome} adicionado com sucesso.')
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar cliente: {e}")

def consultar_produtos(filtro=None):
    query = session.query(Produto)
    if filtro:
        query = query.filter(Produto.nome.ilike(f'%{filtro}%'))
    return query.all()

def realizar_pedido(cliente_id, produtos_quantidades):
    try:
        cliente = session.query(Cliente).get(cliente_id)
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        produtos = []
        valor_total = 0
        for produto_id, quantidade in produtos_quantidades.items():
            produto = session.query(Produto).get(produto_id)
            if not produto:
                raise ValueError(f"Produto ID {produto_id} não encontrado.")
            if produto.estoque < quantidade:
                raise ValueError(f"Estoque insuficiente para o produto {produto.nome}. Estoque disponível: {produto.estoque}")
            
            produtos.append((produto, quantidade))
            valor_total += produto.preco * quantidade

        pedido = Pedido(cliente_id=cliente.id, valor_total=valor_total, status='Pendente')
        session.add(pedido)
        session.commit()  

        for produto, quantidade in produtos:
            produto_pedido = ProdutoPedido(pedido_id=pedido.id, produto_id=produto.id, quantidade=quantidade)
            session.add(produto_pedido)
            produto.estoque -= quantidade

        session.commit()
        print(f"Pedido realizado com sucesso! Pedido ID: {pedido.id}, Valor total: R${valor_total:.2f}")
    except ValueError as ve:
        print(f"Erro: {ve}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao realizar pedido: {e}")

def consultar_pedidos(cliente_id):
    return session.query(Pedido).filter_by(cliente_id=cliente_id).all()

def consultar_clientes():
    clientes = session.query(Cliente).all()
    for cliente in clientes:
        print(f'ID: {cliente.id}, Nome: {cliente.nome}, Email: {cliente.email}')

def atualizar_estoque(produto_id, nova_quantidade):
    try:
        produto = session.query(Produto).get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado.")
        if nova_quantidade < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        
        produto.estoque = nova_quantidade
        session.commit()
        print(f'Estoque do produto {produto.nome} atualizado para {nova_quantidade}.')
    except ValueError as ve:
        print(f"Erro: {ve}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao atualizar estoque: {e}")

def status_pagamento(pedido_id):
    try:
        pedido = session.query(Pedido).get(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado.")
        if pedido.status != 'Pendente':
            print("O pedido já foi processado ou está em outro status.")
            return

        valor_pago = float(input(f'Valor a ser pago para o pedido {pedido_id} (Valor Total: {pedido.valor_total}): '))
        if valor_pago < pedido.valor_total:
            raise ValueError("O valor pago é menor que o valor total. O pedido não pode ser processado.")
        elif valor_pago > pedido.valor_total:
            print("O valor pago é maior que o valor total. Ajuste o valor.")
            return

        metodo_pagamento = input("Método de pagamento (Ex: Cartão, Dinheiro, Pix): ")
        pedido.status = 'Pago'
        pagamento = Pagamento(pedido_id=pedido.id, valor_pago=valor_pago, metodo_pagamento=metodo_pagamento)
        session.add(pagamento)
        session.commit()
        print(f'O Status do pedido {pedido_id} é PAGO')
    except ValueError as ve:
        print(f"Erro: {ve}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao processar pagamento: {e}")


def excluir_produto(produto_id):
    try:
        produto = session.query(Produto).get(produto_id)
        if not produto:
            raise ValueError("Produto não encontrado.")
        
        session.delete(produto)
        session.commit()
        print(f'Produto ID {produto_id} foi excluído.')
    except ValueError as ve:
        print(f"Erro: {ve}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao excluir produto: {e}")

def cancelar_pedido(id_pedido):
    try:
        pedido = session.query(Pedido).get(id_pedido)
        if not pedido:
            raise ValueError("Pedido não encontrado.")
        if pedido.status != 'Pendente':
            raise ValueError("O pedido não pode ser cancelado, pois já foi processado.")

        if session.query(Pagamento).filter_by(pedido_id=pedido.id).count() == 0:
            for produto_pedido in pedido.produtos:
                produto = session.query(Produto).get(produto_pedido.produto_id)
                produto.estoque += produto_pedido.quantidade

            pedido.status = 'Cancelado'
            session.commit()
            print(f'Pedido ID {id_pedido} cancelado automaticamente, pois não houve pagamento.')
        else:
            print("Cancelamento do pedido foi abortado.")
    except ValueError as ve:
        print(f"Erro: {ve}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao cancelar pedido: {e}")


def excluir_conta(cliente_id):
    cliente = session.query(Cliente).get(cliente_id)
    if not cliente:
        print("Cliente não encontrado.")
        return
    
    for pedido in cliente.pedidos:
        session.delete(pedido)
    
    session.delete(cliente)
    session.commit()
    print(f'Conta do cliente ID: {cliente_id} excluída com sucesso.')
  
def main():
    while True:
        print('\nEscolha uma opção:')
        print('1. Adicionar Produto')
        print('2. Adicionar Cliente')
        print('3. Consultar Produtos')
        print('4. Realizar Pedido')
        print('5. Consultar Pedidos')
        print('6. Consultar Clientes')
        print('7. Atualizar estoque')
        print('8. Realizar pagamento')
        print('9. Excluir produto')
        print('10. Cancelar pedido')
        print('11. Excluir conta')
        print('12. Sair')

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
            consultar_clientes()
        elif opcao == '7':
            produto_id = int(input('ID do Produto a ser atualizado: '))
            nova_quantidade = int(input('Nova quantidade em estoque: '))
            atualizar_estoque(produto_id, nova_quantidade)
        elif opcao == '8':  
            pedido_id = int(input('ID do Pedido a ser pago: '))
            status_pagamento(pedido_id)
        elif opcao == '9': 
            produto_id = int(input('ID do Produto a ser excluído: '))
            excluir_produto(produto_id)
        elif opcao == '10':
            pedido_id = int(input('ID do Pedido a ser cancelado: '))
            cancelar_pedido(pedido_id)
        elif opcao == '11':  
            cliente_id = int(input('ID do Cliente a ser excluído: '))
            excluir_conta(cliente_id)
        elif opcao == '12':
            break
        else:
            print('Opção inválida. Tente novamente.')
if __name__ == "__main__":
    main()
