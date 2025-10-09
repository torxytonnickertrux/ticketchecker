#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Auditoria de Desempenho para o Sistema de Ingressos
Realiza análises de desempenho no sistema Django, incluindo:
- Tempo de resposta de views críticas
- Eficiência de consultas ao banco de dados
- Uso de cache
- Gargalos de performance
"""

import os
import sys
import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from functools import wraps

# Adiciona o diretório raiz do projeto ao path para importar módulos do Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.urls import URLPattern, URLResolver
    from django.test import Client
    from django.db import connection, reset_queries
    from django.core.cache import cache
except ImportError:
    print("Erro ao importar Django. Verifique se o ambiente virtual está ativado.")
    sys.exit(1)

class PerformanceAuditor:
    """Classe para auditoria de desempenho do sistema"""
    
    def __init__(self, output_file=None):
        """Inicializa o auditor de desempenho"""
        self.results = {
            'view_response_times': [],
            'database_queries': [],
            'cache_efficiency': [],
            'bottlenecks': []
        }
        self.output_file = output_file or os.path.join(
            Path(__file__).resolve().parent.parent, 
            'relatorios', 
            f'performance_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        self.client = Client()
        
    def measure_view_response_time(self, url, method='get', data=None, iterations=3):
        """Mede o tempo de resposta de uma view"""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            if method.lower() == 'get':
                response = self.client.get(url)
            elif method.lower() == 'post':
                response = self.client.post(url, data or {})
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            end_time = time.time()
            times.append(end_time - start_time)
            
            # Pequena pausa para não sobrecarregar o servidor
            time.sleep(0.1)
        
        avg_time = statistics.mean(times)
        
        self.results['view_response_times'].append({
            'url': url,
            'method': method,
            'average_time': avg_time,
            'min_time': min(times),
            'max_time': max(times),
            'status_code': response.status_code
        })
        
        return avg_time
    
    def count_db_queries(self, func):
        """Decorator para contar consultas ao banco de dados"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            reset_queries()
            settings.DEBUG = True  # Necessário para registrar as consultas
            
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            query_count = len(connection.queries)
            query_time = sum(float(q['time']) for q in connection.queries)
            
            self.results['database_queries'].append({
                'function': func.__name__,
                'query_count': query_count,
                'total_query_time': query_time,
                'execution_time': end_time - start_time,
                'queries': connection.queries if query_count < 20 else "Muitas consultas para exibir"
            })
            
            settings.DEBUG = False
            return result
        return wrapper
    
    def test_cache_efficiency(self, key, value, iterations=5):
        """Testa a eficiência do cache"""
        # Limpa o cache para o teste
        cache.delete(key)
        
        # Mede o tempo para definir o valor no cache
        start_time = time.time()
        cache.set(key, value, 60)  # Cache por 60 segundos
        set_time = time.time() - start_time
        
        get_times = []
        hit_rate = 0
        
        # Mede o tempo para recuperar o valor do cache
        for _ in range(iterations):
            start_time = time.time()
            cached_value = cache.get(key)
            get_times.append(time.time() - start_time)
            
            if cached_value == value:
                hit_rate += 1
        
        hit_rate = (hit_rate / iterations) * 100
        
        self.results['cache_efficiency'].append({
            'key': key,
            'set_time': set_time,
            'average_get_time': statistics.mean(get_times),
            'hit_rate': hit_rate
        })
        
        # Limpa o cache após o teste
        cache.delete(key)
        
        return hit_rate
    
    def identify_bottlenecks(self):
        """Identifica gargalos de desempenho com base nos resultados"""
        # Analisa tempos de resposta das views
        slow_views = [
            view for view in self.results['view_response_times'] 
            if view['average_time'] > 0.5  # Views com tempo de resposta > 500ms
        ]
        
        # Analisa consultas ao banco de dados
        inefficient_queries = [
            query for query in self.results['database_queries']
            if query['query_count'] > 10 or query['total_query_time'] > 0.5
        ]
        
        # Analisa eficiência do cache
        cache_issues = [
            cache_test for cache_test in self.results['cache_efficiency']
            if cache_test['hit_rate'] < 90 or cache_test['average_get_time'] > 0.01
        ]
        
        # Registra os gargalos identificados
        if slow_views:
            self.results['bottlenecks'].append({
                'type': 'slow_views',
                'description': 'Views com tempo de resposta lento',
                'items': slow_views
            })
        
        if inefficient_queries:
            self.results['bottlenecks'].append({
                'type': 'inefficient_queries',
                'description': 'Consultas ineficientes ao banco de dados',
                'items': inefficient_queries
            })
        
        if cache_issues:
            self.results['bottlenecks'].append({
                'type': 'cache_issues',
                'description': 'Problemas de eficiência no cache',
                'items': cache_issues
            })
    
    def collect_url_patterns(self, urlpatterns, base=''):
        """Coleta todos os padrões de URL do projeto"""
        urls = []
        
        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                # É um include, coleta recursivamente
                urls.extend(
                    self.collect_url_patterns(pattern.url_patterns, base + str(pattern.pattern))
                )
            elif isinstance(pattern, URLPattern):
                # É um padrão de URL direto
                url = base + str(pattern.pattern)
                # Substitui parâmetros de URL por valores de teste
                url = re.sub(r'<int:(\w+)>', '1', url)
                url = re.sub(r'<str:(\w+)>', 'test', url)
                url = re.sub(r'<slug:(\w+)>', 'test-slug', url)
                url = re.sub(r'<uuid:(\w+)>', '00000000-0000-0000-0000-000000000000', url)
                urls.append(url)
        
        return urls
    
    def audit_views_performance(self):
        """Audita o desempenho das views principais"""
        print("Auditando desempenho das views...")
        
        try:
            from backend.urls import urlpatterns
            urls = self.collect_url_patterns(urlpatterns)
            
            # Filtra URLs que provavelmente são seguras para testar (exclui admin, logout, etc.)
            safe_urls = [
                url for url in urls 
                if not any(pattern in url for pattern in ['admin', 'logout', 'delete', 'remove'])
            ]
            
            # Testa as URLs seguras
            for url in safe_urls[:10]:  # Limita a 10 URLs para não sobrecarregar
                try:
                    avg_time = self.measure_view_response_time(url)
                    print(f"URL: {url} - Tempo médio: {avg_time:.4f}s")
                except Exception as e:
                    print(f"Erro ao testar URL {url}: {str(e)}")
        
        except (ImportError, AttributeError) as e:
            print(f"Erro ao coletar URLs: {str(e)}")
    
    def audit_model_queries(self):
        """Audita consultas comuns nos modelos"""
        print("Auditando consultas ao banco de dados...")
        
        try:
            # Importa modelos do projeto
            from events.models import Event
            from users.models import User
            
            # Define funções para testar
            @self.count_db_queries
            def test_list_events():
                return list(Event.objects.all()[:10])
            
            @self.count_db_queries
            def test_filter_events():
                return list(Event.objects.filter(active=True)[:10])
            
            @self.count_db_queries
            def test_user_query():
                return list(User.objects.all()[:10])
            
            # Executa os testes
            test_list_events()
            test_filter_events()
            test_user_query()
            
        except (ImportError, AttributeError) as e:
            print(f"Erro ao auditar consultas: {str(e)}")
    
    def audit_cache(self):
        """Audita a eficiência do cache"""
        print("Auditando eficiência do cache...")
        
        # Testa diferentes tipos de dados no cache
        self.test_cache_efficiency('string_test', 'valor de teste' * 10)
        self.test_cache_efficiency('dict_test', {'chave1': 'valor1', 'chave2': 'valor2'})
        self.test_cache_efficiency('list_test', list(range(100)))
    
    def run_all_audits(self):
        """Executa todas as auditorias de desempenho"""
        print("Iniciando auditoria de desempenho...")
        
        try:
            self.audit_views_performance()
        except Exception as e:
            print(f"Erro na auditoria de views: {str(e)}")
        
        try:
            self.audit_model_queries()
        except Exception as e:
            print(f"Erro na auditoria de consultas: {str(e)}")
        
        try:
            self.audit_cache()
        except Exception as e:
            print(f"Erro na auditoria de cache: {str(e)}")
        
        # Identifica gargalos com base nos resultados
        self.identify_bottlenecks()
        
        return self.generate_report()
    
    def generate_report(self):
        """Gera um relatório com os resultados da auditoria"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'views_tested': len(self.results['view_response_times']),
                'queries_tested': len(self.results['database_queries']),
                'cache_tests': len(self.results['cache_efficiency']),
                'bottlenecks_found': len(self.results['bottlenecks'])
            },
            'results': self.results
        }
        
        # Cria o diretório de relatórios se não existir
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Salva o relatório em um arquivo JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"Relatório de desempenho gerado: {self.output_file}")
        print(f"Views testadas: {report['summary']['views_tested']}")
        print(f"Consultas testadas: {report['summary']['queries_tested']}")
        print(f"Testes de cache: {report['summary']['cache_tests']}")
        print(f"Gargalos encontrados: {report['summary']['bottlenecks_found']}")
        
        return report

if __name__ == "__main__":
    import re  # Importação necessária para collect_url_patterns
    auditor = PerformanceAuditor()
    auditor.run_all_audits()