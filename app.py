from flask import Flask, render_template, url_for, request, redirect, flash
import Cadastro

Cadastro.PrepararBanco()

app = Flask(__name__)

# secret_key apenas para o flash
app.secret_key = '12345'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':

        idAviao = int(request.form['idAviao'])
        idCidadeOrigem = int(request.form['idCidadeOrigem'])
        idCidadeDestino = int(request.form['idCidadeDestino'])
        data = request.form['data']
        data = data.split('-')
        ano, mes, dia = list(map(int, data))
        horario = int(request.form['horario'])
        duracao = int(request.form['duracao'])

        try:
            Cadastro.CadastrarVoo(idAviao, idCidadeOrigem, idCidadeDestino, ano, mes, dia, horario, duracao)
        except Cadastro.ExisteErro as e:
            print(e)
            flash('Aviao/Cidade Origem/Cidade Destino nao existe(m)')
        except Cadastro.CidadeErro as e:
            print(e)
            flash('Aviao nao esta nessa Cidade Origem')
        except Cadastro.DataErro as e:
            print(e)
            flash('Aviao nao esta pronto para decolar nesse horario')
        except Cadastro.MesmaCidadeErro as e:
            print(e)
            flash('Cidade de Destino nao pode ser a mesma que a Cidade de Origem')
        except Cadastro.HorarioErro as e:
            print(e)
            flash("Nao é permitido passar duracoes de voo negativas")

        return redirect('/')

    else:
        voos = Cadastro.TodosOsVoos()
        avioes = Cadastro.TodosOsAvioes()
        cidades = Cadastro.TodasAsCidades()
        return render_template('index.html', voos=voos, avioes=avioes, cidades=cidades)

# fazer paginas para cadastrar avioes e cidades
# ver se os nomes sao diferentes de outros avioes/cidades (?)
@app.route('/cadastroAviao', methods=['POST', 'GET'])
def cadastroAviao():
    avioes = Cadastro.TodosOsAvioes()

    if request.method == 'POST':
        
        nome = request.form['nome']

        try:
            Cadastro.CadastrarAviao(nome)
        except Cadastro.ExisteErro as e:
            print(e)
            flash("Aviao com o mesmo nome de outro aviao")

        return redirect('/cadastroAviao')

    else:
        return render_template('avioes.html', avioes=avioes)

@app.route('/cadastroCidade', methods=['POST', 'GET'])
def cadastroCidade():
    cidades = Cadastro.TodasAsCidades()

    if request.method == 'POST':

        nome = request.form['nome']

        try:
            Cadastro.CadastrarCidade(nome)
        except Cadastro.ExisteErro as e:
            print(e)
            flash("Cidade com o mesmo nome de outra cidade")

        return redirect('/cadastroCidade')
    else:
        return render_template('cidades.html', cidades=cidades)


@app.route('/editarAviao/<int:idAviao>', methods=['POST', 'GET'])
def editarAviao(idAviao):

    aviao = Cadastro.PegarAviao(idAviao)

    if request.method == 'POST':
        novoNome = request.form['nome']

        try:
            Cadastro.EditarAviao(idAviao, novoNome)
        except Cadastro.ExisteErro as e:
            print(e)
            flash("Aviao com o mesmo nome ja existe")
        
        return redirect(f'/editarAviao/{idAviao}')
    else:
        return render_template(f'editarAviao.html', aviao=aviao)

@app.route('/editarCidade/<int:idCidade>', methods=['POST', 'GET'])
def editarCidade(idCidade):

    cidade = Cadastro.PegarCidade(idCidade)

    if request.method == 'POST':
        novoNome = request.form['nome']

        try:
            Cadastro.EditarCidade(idCidade, novoNome)
        except Cadastro.ExisteErro as e:
            print(e)
            flash("Cidade com o mesmo nome ja existe")
        
        return redirect(f'/editarCidade/{idCidade}')
    else:
        return render_template(f'editarCidade.html', cidade=cidade)


if __name__ == "__main__":
    app.run(debug=True)

    