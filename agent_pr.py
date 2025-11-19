import os
import sys
import subprocess
from datetime import datetime, timezone
from dotenv import load_dotenv
from github import Github
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown

# Carrega variáveis de ambiente (crie um arquivo .env com GITHUB_TOKEN=seu_token)
load_dotenv()

console = Console()

class GitHubAgent:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            console.print("[bold red]Erro:[/bold red] GITHUB_TOKEN não encontrado no arquivo .env ou variáveis de ambiente.")
            sys.exit(1)
        
        self.g = Github(self.token)
        self.repo = self._get_current_repo()

    def _get_git_output(self, command):
        """Executa comandos git locais"""
        try:
            return subprocess.check_output(command, shell=True).decode().strip()
        except subprocess.CalledProcessError:
            return None

    def _get_current_repo(self):
        """Identifica o repositório atual baseado no git remote"""
        try:
            remote_url = self._get_git_output("git config --get remote.origin.url")
            if not remote_url:
                console.print("[bold red]Erro:[/bold red] Não é um repositório git ou não tem remote configurado.")
                sys.exit(1)
            
            # Tratamento para URLs SSH (git@github.com:user/repo.git) e HTTPS
            repo_name = remote_url.split("github.com")[-1].replace(":", "").replace(".git", "").strip("/")
            return self.g.get_repo(repo_name)
        except Exception as e:
            console.print(f"[bold red]Erro ao conectar com o repositório:[/bold red] {e}")
            sys.exit(1)

    def _generate_pr_body(self, context, changes, testing):
        """Gera um corpo de PR baseado em boas práticas"""
        return f"""
## 📋 Contexto
{context}

## 🛠️ O que foi feito
{changes}

## 🧪 Como testar
{testing}

## ✅ Checklist de Boas Práticas
- [ ] O código segue o style guide do projeto
- [ ] Testes unitários foram criados/atualizados
- [ ] Documentação atualizada
"""

    def create_pr(self):
        """Fluxo interativo para criar um PR com boas práticas"""
        current_branch = self._get_git_output("git rev-parse --abbrev-ref HEAD")
        
        console.print(Panel(f"[bold blue]Criando PR para a branch:[/bold blue] {current_branch}", title="Agent PR"))

        # Coleta de informações para garantir qualidade
        title = Prompt.ask("Título do PR (use Conventional Commits ex: feat: add user login)")
        
        console.print("\n[italic]Vamos preencher o template de boas práticas:[/italic]")
        context = Prompt.ask("1. Qual o contexto? (Por que essa mudança é necessária?)")
        changes = Prompt.ask("2. O que foi alterado tecnicamente?")
        testing = Prompt.ask("3. Como o revisor pode testar essa funcionalidade?")
        
        base_branch = Prompt.ask("Branch de destino", default="main")

        if Confirm.ask(f"Deseja abrir o PR de '{current_branch}' para '{base_branch}'?"):
            body = self._generate_pr_body(context, changes, testing)
            
            try:
                pr = self.repo.create_pull(
                    title=title,
                    body=body,
                    head=current_branch,
                    base=base_branch
                )
                console.print(f"\n[bold green]Sucesso![/bold green] PR criado: {pr.html_url}")
            except Exception as e:
                console.print(f"[bold red]Falha ao criar PR:[/bold red] {e}")

    def list_stale_prs(self):
        """Lista PRs e mostra o contador de tempo (SLA)"""
        prs = self.repo.get_pulls(state='open', sort='created', direction='asc')
        
        table = Table(title=f"Status dos PRs - {self.repo.full_name}")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Título", style="white")
        table.add_column("Autor", style="magenta")
        table.add_column("Tempo Aguardando", justify="right")
        table.add_column("Status", justify="center")

        now = datetime.now(timezone.utc)

        for pr in prs:
            created_at = pr.created_at.replace(tzinfo=timezone.utc)
            duration = now - created_at
            
            days = duration.days
            hours = duration.seconds // 3600
            time_str = f"{days}d {hours}h"

            # Lógica do Contador / Semáforo
            if days >= 3:
                time_style = "[bold red]" # Crítico
                status_emoji = "🔥 Crítico"
            elif days >= 1:
                time_style = "[bold yellow]" # Atenção
                status_emoji = "⚠️ Atenção"
            else:
                time_style = "[bold green]" # Recente
                status_emoji = "🆕 Novo"

            table.add_row(
                str(pr.number),
                pr.title,
                pr.user.login,
                f"{time_style}{time_str}[/]",
                status_emoji
            )

        console.print(table)

if __name__ == "__main__":
    agent = GitHubAgent()
    
    if len(sys.argv) < 2:
        console.print("Uso: python agent_pr.py [create | status]")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "create":
        agent.create_pr()
    elif command == "status":
        agent.list_stale_prs()
    else:
        console.print("[red]Comando desconhecido.[/red] Use 'create' ou 'status'.")
