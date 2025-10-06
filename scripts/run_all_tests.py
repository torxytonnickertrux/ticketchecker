#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema de pagamentos
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Configurar diretório base
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)


class TestRunner:
    """
    Executor de todos os testes
    """
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.results = []
    
    def run_script(self, script_name, description):
        """Executar script de teste"""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        
        script_path = self.base_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Script não encontrado: {script_name}")
            return False
        
        try:
            start_time = time.time()
            
            # Executar script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Exibir resultado
            if result.returncode == 0:
                print(f"✅ {description} - SUCESSO ({duration:.2f}s)")
                print("📄 Saída:")
                print(result.stdout)
            else:
                print(f"❌ {description} - FALHOU ({duration:.2f}s)")
                print("📄 Erro:")
                print(result.stderr)
                print("📄 Saída:")
                print(result.stdout)
            
            self.results.append({
                'script': script_name,
                'description': description,
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT (5 minutos)")
            self.results.append({
                'script': script_name,
                'description': description,
                'success': False,
                'duration': 300,
                'stdout': '',
                'stderr': 'Timeout após 5 minutos'
            })
            return False
            
        except Exception as e:
            print(f"💥 {description} - ERRO: {e}")
            self.results.append({
                'script': script_name,
                'description': description,
                'success': False,
                'duration': 0,
                'stdout': '',
                'stderr': str(e)
            })
            return False
    
    def run_webhook_tests(self):
        """Executar testes de webhook"""
        return self.run_script(
            'test_webhook.py',
            'Testes de Webhook - Conectividade e Endpoints'
        )
    
    def run_comprehensive_tests(self):
        """Executar testes abrangentes"""
        return self.run_script(
            'test_comprehensive_payment.py',
            'Testes Abrangentes - Sistema Completo de Pagamentos'
        )
    
    def run_credit_card_tests(self):
        """Executar testes de cartão de crédito"""
        return self.run_script(
            'test_credit_cards.py',
            'Testes de Cartão de Crédito - Todos os Cenários'
        )
    
    def run_system_monitoring(self):
        """Executar monitoramento do sistema"""
        return self.run_script(
            'monitor_system.py',
            'Monitoramento do Sistema - Saúde e Performance'
        )
    
    def run_production_setup(self):
        """Executar configuração de produção"""
        return self.run_script(
            'setup_production.py',
            'Configuração de Produção - Setup Completo'
        )
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 Iniciando execução de todos os testes")
        print("=" * 70)
        
        # Lista de testes
        tests = [
            ("Webhook Tests", self.run_webhook_tests),
            ("Comprehensive Tests", self.run_comprehensive_tests),
            ("Credit Card Tests", self.run_credit_card_tests),
            ("System Monitoring", self.run_system_monitoring),
            ("Production Setup", self.run_production_setup),
        ]
        
        # Executar testes
        for test_name, test_func in tests:
            print(f"\n🔄 Executando: {test_name}")
            test_func()
        
        # Gerar relatório final
        self.generate_final_report()
    
    def generate_final_report(self):
        """Gerar relatório final"""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL DE TESTES")
        print("=" * 70)
        
        # Estatísticas
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        total_duration = sum(r['duration'] for r in self.results)
        
        print(f"Total de testes: {total_tests}")
        print(f"Testes bem-sucedidos: {successful_tests}")
        print(f"Testes falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        print(f"Tempo total: {total_duration:.2f}s")
        
        # Detalhes por teste
        print(f"\n📋 DETALHES POR TESTE:")
        print("-" * 70)
        
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            duration = result['duration']
            description = result['description']
            
            print(f"{status} {description} ({duration:.2f}s)")
            
            if not result['success'] and result['stderr']:
                print(f"   Erro: {result['stderr'][:100]}...")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        print("-" * 70)
        
        if successful_tests == total_tests:
            print("🎉 Todos os testes passaram! Sistema pronto para produção.")
            print("📋 Próximos passos:")
            print("   1. Configurar webhooks no Mercado Pago")
            print("   2. Testar com dados reais")
            print("   3. Monitorar logs em produção")
            print("   4. Configurar alertas de monitoramento")
        else:
            print("⚠️ Alguns testes falharam. Ações recomendadas:")
            print("   1. Revisar logs de erro acima")
            print("   2. Verificar configurações do sistema")
            print("   3. Executar testes individuais para debug")
            print("   4. Corrigir problemas antes de ir para produção")
        
        # Salvar relatório
        self.save_report()
    
    def save_report(self):
        """Salvar relatório em arquivo"""
        report_file = self.base_dir / 'test_report.txt'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE TESTES DO SISTEMA DE PAGAMENTOS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de testes: {len(self.results)}\n")
                f.write(f"Testes bem-sucedidos: {sum(1 for r in self.results if r['success'])}\n")
                f.write(f"Testes falharam: {sum(1 for r in self.results if not r['success'])}\n\n")
                
                f.write("DETALHES POR TESTE:\n")
                f.write("-" * 30 + "\n")
                
                for result in self.results:
                    status = "SUCESSO" if result['success'] else "FALHOU"
                    f.write(f"{result['description']}: {status} ({result['duration']:.2f}s)\n")
                    
                    if not result['success']:
                        f.write(f"  Erro: {result['stderr']}\n")
                
                f.write("\nLOGS COMPLETOS:\n")
                f.write("-" * 30 + "\n")
                
                for result in self.results:
                    f.write(f"\n{result['description']}:\n")
                    f.write(f"Saída: {result['stdout']}\n")
                    if result['stderr']:
                        f.write(f"Erro: {result['stderr']}\n")
            
            print(f"\n📄 Relatório salvo em: {report_file}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")


def main():
    """Função principal"""
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()