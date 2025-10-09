#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para executar todas as auditorias do sistema de ingressos
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_audit(script_path, description):
    """Executa um script de auditoria e retorna o status"""
    print(f"\n{'=' * 80}")
    print(f"Executando {description}...")
    print(f"{'=' * 80}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {description}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Função principal para executar todas as auditorias"""
    # Obtém o diretório base da auditoria
    base_dir = Path(__file__).resolve().parent
    
    # Define os caminhos para os scripts de auditoria
    security_script = base_dir / "seguranca" / "security_audit.py"
    performance_script = base_dir / "desempenho" / "performance_audit.py"
    data_script = base_dir / "dados" / "data_integrity_audit.py"
    
    # Cria o diretório de relatórios se não existir
    reports_dir = base_dir / "relatorios"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Executa cada auditoria
    results = {}
    results["segurança"] = run_audit(security_script, "Auditoria de Segurança")
    results["desempenho"] = run_audit(performance_script, "Auditoria de Desempenho")
    results["integridade de dados"] = run_audit(data_script, "Auditoria de Integridade de Dados")
    
    # Gera um relatório resumido
    summary_file = reports_dir / f"resumo_auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"Resumo da Auditoria - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        for audit_type, success in results.items():
            status = "✅ Concluída com sucesso" if success else "❌ Falhou"
            f.write(f"Auditoria de {audit_type}: {status}\n")
        
        f.write("\nOs relatórios detalhados estão disponíveis no diretório 'relatorios'.\n")
    
    print(f"\n{'=' * 80}")
    print(f"Todas as auditorias foram concluídas. Resumo salvo em: {summary_file}")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()