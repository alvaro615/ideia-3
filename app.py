import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from database import LibraryManager

# Inicializa DB
db = LibraryManager()

# Escolhendo tema Lux do Bootswatch
BOOTSTRAP_THEME = "https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/lux/bootstrap.min.css"

app = dash.Dash(
    __name__,
    external_stylesheets=[BOOTSTRAP_THEME],
    suppress_callback_exceptions=True
)
server = app.server

# Cards
card_class = dbc.Card([
    dbc.CardHeader("Cadastro de Turma"),
    dbc.CardBody([
        dbc.Input(id="input-class", placeholder="Nome da turma"),
        dbc.Button([html.I(className="fa fa-plus me-2"), "Salvar"],
                   id="btn-add-class", color="primary", className="mt-2"),
        dbc.Alert(id="alert-class", is_open=False, duration=3000)
    ])
], className="mb-4")

card_subject = dbc.Card([
    dbc.CardHeader("Cadastro de Matéria"),
    dbc.CardBody([
        dbc.Input(id="input-subject", placeholder="Nome da matéria"),
        dbc.Button([html.I(className="fa fa-plus me-2"), "Salvar"],
                   id="btn-add-subject", color="secondary", className="mt-2"),
        dbc.Alert(id="alert-subject", is_open=False, duration=3000)
    ])
], className="mb-4")

card_student = dbc.Card([
    dbc.CardHeader("Cadastro de Aluno"),
    dbc.CardBody([
        dbc.Input(id="input-student", placeholder="Nome do aluno"),
        dcc.Dropdown(id="dd-class-student", placeholder="Selecione turma"),
        dbc.Button([html.I(className="fa fa-user-plus me-2"), "Salvar"],
                   id="btn-add-student", color="primary", className="mt-2"),
        dbc.Alert(id="alert-student", is_open=False, duration=3000)
    ])
], className="mb-4")

card_book = dbc.Card([
    dbc.CardHeader("Cadastro de Livro"),
    dbc.CardBody([
        dbc.Input(id="input-book-title", placeholder="Título"),
        dbc.Input(id="input-book-author", placeholder="Autor", className="mt-2"),
        dcc.Dropdown(id="dd-class-book", placeholder="Turma", className="mt-2"),
        dcc.Dropdown(id="dd-subject-book", placeholder="Matéria", className="mt-2"),
        dbc.Button([html.I(className="fa fa-book-medical me-2"), "Salvar"],
                   id="btn-add-book", color="secondary", className="mt-2"),
        dbc.Alert(id="alert-book", is_open=False, duration=3000)
    ])
], className="mb-4")

card_assign = dbc.Card([
    dbc.CardHeader("Atribuir Livro"),
    dbc.CardBody([
        dcc.Dropdown(id="dd-class-assign", placeholder="Turma"),
        dcc.Dropdown(id="dd-student-assign", placeholder="Aluno", className="mt-2"),
        dcc.Dropdown(id="dd-subject-assign", placeholder="Matéria", className="mt-2"),
        dcc.Dropdown(id="dd-book-assign", placeholder="Livro", className="mt-2"),
        dbc.Button([html.I(className="fa fa-hand-paper me-2"), "Atribuir"],
                   id="btn-assign", color="success", className="mt-2"),
        dbc.Alert(id="alert-assign", is_open=False, duration=3000)
    ])
], className="mb-4")

# Layout principal
app.layout = dbc.Container(fluid=True, children=[
    html.H1("Library Manager", className="my-4 text-center"),
    dbc.Tabs(id="tabs", active_tab="tab1", children=[
        dbc.Tab(label="Turmas & Matérias", tab_id="tab1"),
        dbc.Tab(label="Alunos & Livros", tab_id="tab2"),
        dbc.Tab(label="Atribuições", tab_id="tab3"),
    ]),
    html.Div(id="tab-content", className="p-4")
])

# Renderização de abas
@app.callback(Output("tab-content", "children"),
              Input("tabs", "active_tab"))
def render_tab(tab):
    classes = db.list_classes()
    subjects = db.list_subjects()

    if tab == "tab1":
        return dbc.Row([
            dbc.Col(card_class, md=6),
            dbc.Col(card_subject, md=6),
        ])
    elif tab == "tab2":
        # popula dropdowns iniciais
        return dbc.Row([
            dbc.Col(card_student, md=6),
            dbc.Col(card_book, md=6),
        ])
    else:
        return html.Div([
            card_assign,
            html.H5("Atribuições Existentes", className="mt-4"),
            dcc.Dropdown(
                id="dd-class-report",
                options=[{"label": c[1], "value": c[0]} for c in classes],
                placeholder="Filtrar por turma",
                className="mb-2"
            ),
            dbc.Table(id="table-assignments", bordered=True, striped=True)
        ])

# Callbacks de CRUD e UI
@app.callback(
    Output("alert-class", "children"),
    Output("alert-class", "color"),
    Output("alert-class", "is_open"),
    Input("btn-add-class", "n_clicks"),
    State("input-class", "value"),
    prevent_initial_call=True
)
def add_class(n, name):
    if name:
        db.add_class(name)
        return "Turma adicionada!", "success", True
    return "Preencha o nome.", "danger", True

@app.callback(
    Output("alert-subject", "children"),
    Output("alert-subject", "color"),
    Output("alert-subject", "is_open"),
    Input("btn-add-subject", "n_clicks"),
    State("input-subject", "value"),
    prevent_initial_call=True
)
def add_subject(n, name):
    if name:
        db.add_subject(name)
        return "Matéria adicionada!", "success", True
    return "Preencha o nome.", "danger", True

@app.callback(
    Output("dd-class-student", "options"),
    Input("tabs", "active_tab")
)
def update_class_student(tab):
    return [{"label": c[1], "value": c[0]} for c in db.list_classes()]

@app.callback(
    Output("alert-student", "children"),
    Output("alert-student", "color"),
    Output("alert-student", "is_open"),
    Input("btn-add-student", "n_clicks"),
    State("input-student", "value"),
    State("dd-class-student", "value"),
    prevent_initial_call=True
)
def add_student(n, name, class_id):
    if name and class_id:
        db.add_student(name, class_id)
        return "Aluno adicionado!", "success", True
    return "Preencha todos os campos.", "danger", True

@app.callback(
    Output("dd-class-book", "options"),
    Output("dd-subject-book", "options"),
    Input("tabs", "active_tab")
)
def update_book_dropdowns(tab):
    return (
        [{"label": c[1], "value": c[0]} for c in db.list_classes()],
        [{"label": s[1], "value": s[0]} for s in db.list_subjects()]
    )

@app.callback(
    Output("alert-book", "children"),
    Output("alert-book", "color"),
    Output("alert-book", "is_open"),
    Input("btn-add-book", "n_clicks"),
    State("input-book-title", "value"),
    State("input-book-author", "value"),
    State("dd-class-book", "value"),
    State("dd-subject-book", "value"),
    prevent_initial_call=True
)
def add_book(n, title, author, class_id, subject_id):
    if title and author and class_id and subject_id:
        db.add_book(title, author, class_id, subject_id)
        return "Livro adicionado!", "success", True
    return "Preencha todos os campos.", "danger", True

@app.callback(
    Output("dd-student-assign", "options"),
    Input("dd-class-assign", "value")
)
def load_students(class_id):
    if class_id:
        return [{"label": s[1], "value": s[0]} for s in db.list_students(class_id)]
    return []

@app.callback(
    Output("dd-subject-assign", "options"),
    Input("dd-class-assign", "value")
)
def load_subjects(class_id):
    if class_id:
        return [{"label": s[1], "value": s[0]} for s in db.list_subjects()]
    return []

@app.callback(
    Output("dd-book-assign", "options"),
    Input("dd-class-assign", "value"),
    Input("dd-subject-assign", "value")
)
def load_books(class_id, subject_id):
    if class_id and subject_id:
        return [{"label": b[1], "value": b[0]} for b in db.list_books(class_id, subject_id)]
    return []

@app.callback(
    Output("alert-assign", "children"),
    Output("alert-assign", "color"),
    Output("alert-assign", "is_open"),
    Output("table-assignments", "children"),
    Input("btn-assign", "n_clicks"),
    State("dd-student-assign", "value"),
    State("dd-book-assign", "value"),
    State("dd-class-report", "value"),
    prevent_initial_call=True
)
def do_assign(n, student_id, book_id, report_class_id):
    msg, color = ("Livro atribuído!", "success") if db.assign_book(student_id, book_id) else ("Falha na atribuição.", "danger")
    # tabela de atribuições
    data = db.list_assignments(report_class_id)
    header = [html.Thead(html.Tr([html.Th(col) for col in ["Turma","Aluno","Matéria","Livro"]]))]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in data]
    body = [html.Tbody(rows)]
    return msg, color, True, header + body

if __name__ == "__main__":
    app.run(debug=True, port=8050)