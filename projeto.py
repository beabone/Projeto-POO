from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

engine = create_engine('sqlite:///biblioteca.db')
Session = sessionmaker(bind=engine)
session = Session()

class Produto:
   __tablename__ = 'Produtos'
   
   id = Column 
   nome = Column
   preço = Column
   marca = Column
   estoque_disponivel = Column

    
class Cliente(Produto):
    __tablename__ = 'Clientes'
    
    cpf =  Column
    nome = Column
    telefone = Column
    historico_de_compras = Column
    produto_id = Column
    produto = relationship ('Produto', backref = 'clientes')
    
Base.metadata.create_all(engine)
    
def adicionar_produto(produto_nome, preço, marca, estoque_disponivel):
    produto = session.query(Produto).filter_by(nome= produto_nome).first()
    if not produto:
        print(f'Produto "{produto_nome}" não encontrado.')
        return
    
    produto = Produto(produto = produto)
    session.add(produto)
    session.commit()
    
def 
        return sum(produto.preço for produto in self.produtos_comprados)
