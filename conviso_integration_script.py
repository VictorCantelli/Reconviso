#!/usr/bin/env python3
"""
Conviso Platform Integration - GraphQL API
Integração completa para envio de findings de OSINT recon
"""

import json
import os
import sys
import requests
from typing import List, Dict, Any
from datetime import datetime


class ConvisoIntegration:
    """Cliente para integração com Conviso Platform via GraphQL"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.convisoappsec.com/graphql"):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "x-api-key": api_key  # Algumas APIs usam este header
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Executa uma query GraphQL"""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = self.session.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                print(f"❌ GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
                return None
            
            return data.get("data")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            return None
    
    def get_or_create_project(self, name: str, target_url: str) -> str:
        """Busca ou cria um projeto no Conviso"""
        
        # Query para buscar projeto existente
        search_query = """
        query SearchProject($name: String!) {
          projects(filter: {name: {eq: $name}}) {
            collection {
              id
              name
            }
          }
        }
        """
        
        result = self.execute_query(search_query, {"name": name})
        
        if result and result.get("projects", {}).get("collection"):
            projects = result["projects"]["collection"]
            if projects:
                project_id = projects[0]["id"]
                print(f"✅ Projeto encontrado: {name} (ID: {project_id})")
                return project_id
        
        # Se não existe, criar novo projeto
        create_mutation = """
        mutation CreateProject($input: CreateProjectInput!) {
          createProject(input: $input) {
            project {
              id
              name
            }
            errors
          }
        }
        """
        
        variables = {
            "input": {
                "name": name,
                "description": f"OSINT Recon automated scan for {target_url}",
                "projectType": "WEB_APPLICATION"
            }
        }
        
        result = self.execute_query(create_mutation, variables)
        
        if result and result.get("createProject"):
            project_id = result["createProject"]["project"]["id"]
            print(f"✅ Projeto criado: {name} (ID: {project_id})")
            return project_id
        
        print(f"❌ Falha ao criar projeto: {name}")
        return None
    
    def create_vulnerability(self, project_id: str, finding: Dict) -> bool:
        """Cria uma vulnerabilidade no Conviso"""
        
        mutation = """
        mutation CreateVulnerability($input: CreateVulnerabilityInput!) {
          createVulnerability(input: $input) {
            vulnerability {
              id
              title
              identifier
              severity
            }
            errors
          }
        }
        """
        
        # Mapear severidade para formato Conviso
        severity_map = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
            "info": "INFORMATIONAL"
        }
        
        # Preparar descrição detalhada
        description = self._format_description(finding)
        
        variables = {
            "input": {
                "projectId": project_id,
                "title": finding.get("name", "Unknown Vulnerability"),
                "identifier": finding.get("template_id", "OSINT-RECON"),
                "severity": severity_map.get(finding.get("severity", "info"), "INFORMATIONAL"),
                "description": description,
                "vulnerabilityType": "INFORMATION_DISCLOSURE",  # Ajustar conforme necessário
                "status": "IDENTIFIED",
                "discoveredAt": finding.get("timestamp", datetime.utcnow().isoformat()),
                "affectedResource": finding.get("matched_at", ""),
                "tags": finding.get("tags", [])
            }
        }
        
        result = self.execute_query(mutation, variables)
        
        if result and result.get("createVulnerability"):
            vuln = result["createVulnerability"]["vulnerability"]
            if vuln:
                print(f"  ✅ Vulnerability criada: {vuln['title']} ({vuln['severity']})")
                return True
            else:
                errors = result["createVulnerability"].get("errors", [])
                print(f"  ❌ Erro ao criar: {errors}")
        
        return False
    
    def _format_description(self, finding: Dict) -> str:
        """Formata descrição da vulnerabilidade com todos os detalhes"""
        
        description = f"""## {finding.get('name', 'Unknown')}

**Template ID:** `{finding.get('template_id', 'N/A')}`
**Severity:** {finding.get('severity', 'info').upper()}
**Discovered:** {finding.get('timestamp', 'N/A')}

### Description
{finding.get('description', 'No description available')}

### Location
**Matched at:** `{finding.get('matched_at', 'N/A')}`

"""
        
        # Adicionar resultados extraídos
        if finding.get('extracted_results'):
            description += "### Extracted Data\n```\n"
            description += "\n".join(finding['extracted_results'])
            description += "\n```\n\n"
        
        # Adicionar comando curl para reprodução
        if finding.get('curl_command'):
            description += "### Reproduction\n```bash\n"
            description += finding['curl_command']
            description += "\n```\n\n"
        
        # Tags
        if finding.get('tags'):
            description += f"**Tags:** {', '.join(finding['tags'])}\n"
        
        # Source
        description += f"\n---\n*Generated by OSINT Recon Pipeline - Scan ID: {finding.get('scan_id', 'N/A')}*"
        
        return description
    
    def create_scan_summary(self, project_id: str, summary: Dict) -> bool:
        """Cria um sumário do scan como nota no projeto"""
        
        # Criar nota com sumário do scan
        mutation = """
        mutation CreateNote($input: CreateNoteInput!) {
          createNote(input: $input) {
            note {
              id
              title
            }
            errors
          }
        }
        """
        
        content = f"""# OSINT Recon Scan Summary

**Scan ID:** {summary.get('scan_id', 'N/A')}
**Target:** {summary.get('target', 'N/A')}
**Total Findings:** {summary.get('total_findings', 0)}
**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Severity Breakdown
"""
        
        for severity, count in sorted(summary.get('severity_breakdown', {}).items()):
            content += f"- **{severity.upper()}**: {count}\n"
        
        content += "\n*This summary was automatically generated by the OSINT Recon Pipeline*"
        
        variables = {
            "input": {
                "projectId": project_id,
                "title": f"OSINT Scan - {summary.get('scan_id')}",
                "content": content
            }
        }
        
        result = self.execute_query(mutation, variables)
        
        if result and result.get("createNote"):
            print(f"✅ Scan summary created")
            return True
        
        return False
    
    def process_findings_file(self, findings_file: str) -> bool:
        """Processa arquivo de findings e envia para Conviso"""
        
        print(f"\n🔄 Processando findings de: {findings_file}\n")
        
        try:
            with open(findings_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return False
        
        target = data.get('target', 'Unknown Target')
        scan_id = data.get('scan_id', 'Unknown')
        findings = data.get('findings', [])
        
        if not findings:
            print("⚠️  Nenhum finding para processar")
            return True
        
        # Criar ou buscar projeto
        project_name = f"OSINT - {target.replace('https://', '').replace('http://', '')}"
        project_id = self.get_or_create_project(project_name, target)
        
        if not project_id:
            print("❌ Não foi possível criar/encontrar projeto")
            return False
        
        # Criar sumário do scan
        self.create_scan_summary(project_id, data)
        
        # Processar findings
        success_count = 0
        failure_count = 0
        
        print(f"\n📤 Enviando {len(findings)} findings...\n")
        
        # Filtrar apenas severidades relevantes
        relevant_findings = [
            f for f in findings 
            if f.get('severity') in ['critical', 'high', 'medium']
        ]
        
        print(f"🔍 Findings relevantes (critical/high/medium): {len(relevant_findings)}")
        
        for i, finding in enumerate(relevant_findings, 1):
            print(f"[{i}/{len(relevant_findings)}] {finding.get('name', 'Unknown')[:60]}...")
            
            if self.create_vulnerability(project_id, finding):
                success_count += 1
            else:
                failure_count += 1
        
        print(f"\n" + "="*50)
        print(f"✅ Sucesso: {success_count}")
        print(f"❌ Falhas: {failure_count}")
        print(f"📊 Total processado: {len(relevant_findings)}")
        print("="*50 + "\n")
        
        return failure_count == 0


def main():
    """Função principal"""
    
    if len(sys.argv) < 2:
        print("Usage: python conviso_integration.py <findings-file.json>")
        sys.exit(1)
    
    findings_file = sys.argv[1]
    
    # Obter API key das variáveis de ambiente
    api_key = os.environ.get('CONVISO_API_KEY')
    
    if not api_key:
        print("❌ CONVISO_API_KEY não encontrada nas variáveis de ambiente")
        sys.exit(1)
    
    # Inicializar cliente
    client = ConvisoIntegration(api_key)
    
    # Processar findings
    success = client.process_findings_file(findings_file)
    
    if success:
        print("\n✅ Findings enviados com sucesso para Conviso Platform!")
        sys.exit(0)
    else:
        print("\n❌ Ocorreram erros durante o envio")
        sys.exit(1)


if __name__ == "__main__":
    main()