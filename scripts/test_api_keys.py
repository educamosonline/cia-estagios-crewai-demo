#!/usr/bin/env python3
"""
API Keys Validation Script
==========================

Script para validar todas as chaves de API utilizadas no projeto CE Demo.

Author: CE Demo System
Created: 2025-07-24
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIKeyValidator:
    """Validador de chaves de API."""
    
    def __init__(self):
        self.results = []
        self.load_environment()
    
    def load_environment(self):
        """Carrega variáveis de ambiente."""
        # Try to load from .env file if it exists
        env_file = project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value.strip('"').strip("'")
    
    async def test_openai_api(self) -> Dict[str, Any]:
        """Testa a chave da API OpenAI."""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key.startswith('sk-test'):
            return {
                'service': 'OpenAI',
                'status': 'MISSING',
                'message': 'Chave não configurada ou usando chave de teste',
                'key_preview': api_key[:10] + '...' if api_key else 'None'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': 'Hello'}],
                'max_tokens': 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'service': 'OpenAI',
                            'status': 'VALID',
                            'message': 'Chave válida e funcional',
                            'key_preview': api_key[:10] + '...',
                            'model_used': result.get('model', 'unknown')
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'service': 'OpenAI',
                            'status': 'INVALID',
                            'message': f'Erro HTTP {response.status}: {error_text[:100]}',
                            'key_preview': api_key[:10] + '...'
                        }
                        
        except Exception as e:
            return {
                'service': 'OpenAI',
                'status': 'ERROR',
                'message': f'Erro na conexão: {str(e)}',
                'key_preview': api_key[:10] + '...' if api_key else 'None'
            }
    
    async def test_anthropic_api(self) -> Dict[str, Any]:
        """Testa a chave da API Anthropic."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key.startswith('sk-ant-test'):
            return {
                'service': 'Anthropic',
                'status': 'MISSING',
                'message': 'Chave não configurada ou usando chave de teste',
                'key_preview': api_key[:10] + '...' if api_key else 'None'
            }
        
        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 5,
                'messages': [{'role': 'user', 'content': 'Hello'}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'service': 'Anthropic',
                            'status': 'VALID',
                            'message': 'Chave válida e funcional',
                            'key_preview': api_key[:10] + '...',
                            'model_used': result.get('model', 'unknown')
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'service': 'Anthropic',
                            'status': 'INVALID',
                            'message': f'Erro HTTP {response.status}: {error_text[:100]}',
                            'key_preview': api_key[:10] + '...'
                        }
                        
        except Exception as e:
            return {
                'service': 'Anthropic',
                'status': 'ERROR',
                'message': f'Erro na conexão: {str(e)}',
                'key_preview': api_key[:10] + '...' if api_key else 'None'
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Executa todos os testes de API."""
        print("🔑 CE Demo - Validador de Chaves de API")
        print("=" * 50)
        print(f"Iniciando testes em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run async tests
        async_tests = [
            self.test_openai_api(),
            self.test_anthropic_api()
        ]
        
        results = await asyncio.gather(*async_tests, return_exceptions=True)
        
        # Process results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                valid_results.append({
                    'service': 'Unknown',
                    'status': 'ERROR',
                    'message': f'Erro no teste: {str(result)}',
                    'key_preview': 'None'
                })
            else:
                valid_results.append(result)
        
        self.results = valid_results
        return valid_results
    
    def print_results(self):
        """Imprime os resultados dos testes."""
        print("📊 Resultados da Validação:")
        print("-" * 50)
        
        valid_count = 0
        missing_count = 0
        error_count = 0
        
        for result in self.results:
            status = result['status']
            service = result['service']
            message = result['message']
            key_preview = result.get('key_preview', 'None')
            
            # Status icon
            if status == 'VALID':
                icon = "✅"
                valid_count += 1
            elif status == 'MISSING':
                icon = "⚠️"
                missing_count += 1
            else:
                icon = "❌"
                error_count += 1
            
            print(f"{icon} {service}")
            print(f"   Status: {status}")
            print(f"   Chave: {key_preview}")
            print(f"   Detalhes: {message}")
            
            # Additional info
            if 'model_used' in result:
                print(f"   Modelo testado: {result['model_used']}")
            
            print()
        
        # Summary
        print("📈 Resumo:")
        print(f"   ✅ APIs válidas: {valid_count}")
        print(f"   ⚠️  APIs não configuradas: {missing_count}")
        print(f"   ❌ APIs com erro: {error_count}")
        print(f"   📊 Total testado: {len(self.results)}")
        
        # Recommendations
        print("\n💡 Recomendações:")
        if missing_count > 0:
            print("   - Configure as chaves de API faltantes no arquivo .env")
        if error_count > 0:
            print("   - Verifique as chaves com erro e sua conectividade")
        if valid_count == len([r for r in self.results if r['status'] != 'MISSING']):
            print("   - Todas as chaves configuradas estão funcionando! 🎉")

async def main():
    """Função principal."""
    validator = APIKeyValidator()
    
    try:
        await validator.run_all_tests()
        validator.print_results()
        
        # Return appropriate exit code
        error_count = len([r for r in validator.results if r['status'] == 'ERROR'])
        if error_count > 0:
            print(f"\n⚠️  {error_count} chave(s) com erro detectada(s)")
            sys.exit(1)
        else:
            print("\n✅ Validação concluída com sucesso!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())