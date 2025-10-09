#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Auditoria de Integridade de Dados para o Sistema de Ingressos
Realiza verificações de integridade nos dados do sistema, incluindo:
- Consistência entre modelos relacionados
- Validação de dados críticos
- Detecção de dados órfãos ou inconsistentes
- Verificação de integridade referencial
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Adiciona o diretório raiz do projeto ao path para importar módulos do Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.db import connection
    from django.db.models import Count, Q, F
    from django.core.exceptions import ValidationError
except ImportError:
    print("Erro ao importar Django. Verifique se o ambiente virtual está ativado.")
    sys.exit(1)

class DataIntegrityAuditor:
    """Classe para auditoria de integridade de dados do sistema"""
    
    def __init__(self, output_file=None):
        """Inicializa o auditor de integridade de dados"""
        self.issues = []
        self.output_file = output_file or os.path.join(
            Path(__file__).resolve().parent.parent, 
            'relatorios', 
            f'data_integrity_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        self.severity_levels = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
    
    def add_issue(self, title, description, severity, affected_records=None, recommendation=None):
        """Adiciona um problema de integridade encontrado"""
        issue = {
            'title': title,
            'description': description,
            'severity': severity,
            'affected_records': affected_records or [],
            'recommendation': recommendation or "Nenhuma recomendação disponível"
        }
        self.issues.append(issue)
        self.severity_levels[severity] += 1
    
    def check_orphaned_records(self):
        """Verifica registros órfãos em modelos relacionados"""
        print("Verificando registros órfãos...")
        
        try:
            # Importa os modelos necessários
            from events.models import Event
            
            # Exemplo: Verificar eventos sem ingressos associados
            try:
                from events.models import Ticket
                
                events_without_tickets = Event.objects.annotate(
                    ticket_count=Count('ticket')
                ).filter(ticket_count=0)
                
                if events_without_tickets.exists():
                    self.add_issue(
                        title="Eventos sem ingressos",
                        description=f"Encontrados {events_without_tickets.count()} eventos sem ingressos associados.",
                        severity="medium",
                        affected_records=[
                            {'id': event.id, 'name': event.name if hasattr(event, 'name') else f"Evento {event.id}"}
                            for event in events_without_tickets[:10]  # Limita a 10 registros
                        ],
                        recommendation="Verifique se estes eventos deveriam ter ingressos ou se podem ser removidos."
                    )
            except (ImportError, AttributeError):
                # Modelo Ticket pode não existir
                pass
            
            # Verificar usuários sem perfil (se aplicável)
            try:
                from django.contrib.auth.models import User
                from users.models import Profile
                
                users_without_profile = User.objects.filter(
                    ~Q(profile__isnull=False)
                )
                
                if users_without_profile.exists():
                    self.add_issue(
                        title="Usuários sem perfil",
                        description=f"Encontrados {users_without_profile.count()} usuários sem perfil associado.",
                        severity="high",
                        affected_records=[
                            {'id': user.id, 'user': getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'name', '') or getattr(user, 'email', '') or str(user)}
                            for user in users_without_profile[:10]  # Limita a 10 registros
                        ],
                        recommendation="Crie perfis para estes usuários ou verifique se são contas de teste."
                    )
            except (ImportError, AttributeError):
                # Modelo Profile pode não existir
                pass
            
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar registros órfãos",
                description=f"Ocorreu um erro durante a verificação: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente a integridade referencial entre os modelos."
            )
    
    def check_data_consistency(self):
        """Verifica consistência de dados entre modelos relacionados"""
        print("Verificando consistência de dados...")
        
        try:
            # Importa os modelos necessários
            from events.models import Event
            
            # Exemplo: Verificar consistência de datas de eventos
            events_with_invalid_dates = Event.objects.filter(
                Q(end_date__lt=F('start_date')) | 
                Q(start_date__isnull=True) |
                Q(end_date__isnull=True)
            )
            
            if events_with_invalid_dates.exists():
                self.add_issue(
                    title="Eventos com datas inconsistentes",
                    description=f"Encontrados {events_with_invalid_dates.count()} eventos com datas inválidas ou nulas.",
                    severity="high",
                    affected_records=[
                        {
                            'id': event.id, 
                            'name': event.name if hasattr(event, 'name') else f"Evento {event.id}",
                            'start_date': str(event.start_date) if hasattr(event, 'start_date') else None,
                            'end_date': str(event.end_date) if hasattr(event, 'end_date') else None
                        }
                        for event in events_with_invalid_dates[:10]  # Limita a 10 registros
                    ],
                    recommendation="Corrija as datas dos eventos para garantir que a data de término seja posterior à data de início."
                )
            
            # Verificar consistência de preços (se aplicável)
            try:
                from events.models import Ticket
                
                tickets_with_invalid_prices = Ticket.objects.filter(
                    Q(price__lt=0) | Q(price__isnull=True)
                )
                
                if tickets_with_invalid_prices.exists():
                    self.add_issue(
                        title="Ingressos com preços inválidos",
                        description=f"Encontrados {tickets_with_invalid_prices.count()} ingressos com preços negativos ou nulos.",
                        severity="critical",
                        affected_records=[
                            {
                                'id': ticket.id,
                                'event': ticket.event.name if hasattr(ticket.event, 'name') else f"Evento {ticket.event.id}",
                                'price': str(ticket.price)
                            }
                            for ticket in tickets_with_invalid_prices[:10]  # Limita a 10 registros
                        ],
                        recommendation="Corrija os preços dos ingressos para valores positivos ou zero."
                    )
            except (ImportError, AttributeError):
                # Modelo Ticket pode não existir
                pass
            
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar consistência de dados",
                description=f"Ocorreu um erro durante a verificação: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente a consistência dos dados entre os modelos relacionados."
            )
    
    def check_data_validation(self):
        """Verifica se os dados atendem às regras de validação dos modelos"""
        print("Verificando validação de dados...")
        
        try:
            # Importa os modelos necessários
            from events.models import Event
            
            # Coleta todos os eventos
            all_events = Event.objects.all()
            invalid_events = []
            
            # Verifica cada evento individualmente
            for event in all_events:
                try:
                    event.full_clean()
                except ValidationError as e:
                    invalid_events.append({
                        'id': event.id,
                        'name': event.name if hasattr(event, 'name') else f"Evento {event.id}",
                        'errors': str(e)
                    })
            
            if invalid_events:
                self.add_issue(
                    title="Eventos com dados inválidos",
                    description=f"Encontrados {len(invalid_events)} eventos que não passam na validação do modelo.",
                    severity="high",
                    affected_records=invalid_events[:10],  # Limita a 10 registros
                    recommendation="Corrija os dados dos eventos para atender às regras de validação do modelo."
                )
            
            # Verifica usuários (se aplicável)
            try:
                from django.contrib.auth.models import User
                
                all_users = User.objects.all()
                invalid_users = []
                
                for user in all_users:
                    try:
                        user.full_clean()
                    except ValidationError as e:
                        invalid_users.append({
                            'id': user.id,
                            'user': getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'name', '') or getattr(user, 'email', '') or str(user),
                            'errors': str(e)
                        })
                
                if invalid_users:
                    self.add_issue(
                        title="Usuários com dados inválidos",
                        description=f"Encontrados {len(invalid_users)} usuários que não passam na validação do modelo.",
                        severity="high",
                        affected_records=invalid_users[:10],  # Limita a 10 registros
                        recommendation="Corrija os dados dos usuários para atender às regras de validação do modelo."
                    )
            except (ImportError, AttributeError):
                pass
            
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar validação de dados",
                description=f"Ocorreu um erro durante a verificação: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente a validação dos dados nos modelos."
            )
    
    def check_database_constraints(self):
        """Verifica restrições de banco de dados usando SQL direto"""
        print("Verificando restrições de banco de dados...")
        
        try:
            with connection.cursor() as cursor:
                # Verifica chaves estrangeiras quebradas (PostgreSQL)
                if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                    cursor.execute("""
                        SELECT conrelid::regclass AS table_name,
                               conname AS constraint_name,
                               pg_get_constraintdef(oid) AS constraint_definition
                        FROM pg_constraint
                        WHERE confrelid IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1
                            FROM pg_constraint AS c2
                            WHERE c2.conrelid = pg_constraint.confrelid
                            AND c2.contype = 'p'
                        );
                    """)
                    broken_constraints = cursor.fetchall()
                    
                    if broken_constraints:
                        self.add_issue(
                            title="Restrições de chave estrangeira quebradas",
                            description=f"Encontradas {len(broken_constraints)} restrições de chave estrangeira que apontam para tabelas sem chave primária.",
                            severity="critical",
                            affected_records=[
                                {
                                    'table': constraint[0],
                                    'constraint': constraint[1],
                                    'definition': constraint[2]
                                }
                                for constraint in broken_constraints
                            ],
                            recommendation="Corrija as restrições de chave estrangeira ou adicione chaves primárias às tabelas referenciadas."
                        )
                
                # Verifica índices duplicados (PostgreSQL)
                if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                    cursor.execute("""
                        SELECT
                            indrelid::regclass AS table_name,
                            array_agg(indexrelid::regclass) AS indexes,
                            array_agg(indkey) AS index_columns
                        FROM pg_index
                        GROUP BY indrelid, indkey
                        HAVING COUNT(*) > 1;
                    """)
                    duplicate_indexes = cursor.fetchall()
                    
                    if duplicate_indexes:
                        self.add_issue(
                            title="Índices duplicados",
                            description=f"Encontrados {len(duplicate_indexes)} conjuntos de índices duplicados.",
                            severity="medium",
                            affected_records=[
                                {
                                    'table': index[0],
                                    'indexes': index[1],
                                    'columns': index[2]
                                }
                                for index in duplicate_indexes
                            ],
                            recommendation="Remova os índices duplicados para melhorar o desempenho do banco de dados."
                        )
        
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar restrições de banco de dados",
                description=f"Ocorreu um erro durante a verificação: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente as restrições de banco de dados."
            )
    
    def check_data_completeness(self):
        """Verifica a completude dos dados em campos importantes"""
        print("Verificando completude dos dados...")
        
        try:
            # Importa os modelos necessários
            from events.models import Event
            
            # Verifica campos nulos em eventos
            null_fields = defaultdict(int)
            
            for field in Event._meta.fields:
                if not field.null:
                    continue  # Pula campos que não permitem nulos
                
                count = Event.objects.filter(**{f"{field.name}__isnull": True}).count()
                if count > 0:
                    null_fields[field.name] = count
            
            if null_fields:
                self.add_issue(
                    title="Campos importantes com valores nulos em eventos",
                    description=f"Encontrados campos com valores nulos em eventos.",
                    severity="medium",
                    affected_records=[
                        {'field': field, 'count': count}
                        for field, count in null_fields.items()
                    ],
                    recommendation="Preencha os campos nulos com valores apropriados."
                )
            
            # Verifica usuários com emails vazios (se aplicável)
            try:
                from django.contrib.auth.models import User
                
                users_without_email = User.objects.filter(
                    Q(email='') | Q(email__isnull=True)
                ).count()
                
                if users_without_email > 0:
                    self.add_issue(
                        title="Usuários sem email",
                        description=f"Encontrados {users_without_email} usuários sem endereço de email.",
                        severity="medium",
                        recommendation="Solicite que os usuários forneçam um endereço de email válido."
                    )
            except (ImportError, AttributeError):
                pass
            
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar completude dos dados",
                description=f"Ocorreu um erro durante a verificação: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente a completude dos dados nos modelos."
            )
    
    def run_all_checks(self):
        """Executa todas as verificações de integridade de dados"""
        print("Iniciando auditoria de integridade de dados...")
        
        checks = [
            self.check_orphaned_records,
            self.check_data_consistency,
            self.check_data_validation,
            self.check_database_constraints,
            self.check_data_completeness
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.add_issue(
                    title=f"Erro ao executar {check.__name__}",
                    description=f"Ocorreu um erro durante a verificação: {str(e)}",
                    severity="info",
                    recommendation="Verifique manualmente este aspecto de integridade de dados."
                )
        
        return self.generate_report()
    
    def generate_report(self):
        """Gera um relatório com os problemas encontrados"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.issues),
                'severity_counts': self.severity_levels
            },
            'issues': self.issues
        }
        
        # Cria o diretório de relatórios se não existir
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Salva o relatório em um arquivo JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"Relatório de integridade de dados gerado: {self.output_file}")
        print(f"Total de problemas encontrados: {len(self.issues)}")
        for severity, count in self.severity_levels.items():
            if count > 0:
                print(f"- {severity.upper()}: {count}")
        
        return report

if __name__ == "__main__":
    auditor = DataIntegrityAuditor()
    auditor.run_all_checks()