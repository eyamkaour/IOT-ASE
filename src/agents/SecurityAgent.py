from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from security import jwt_auth, rbac, request_guard, rate_limit

class UserRole(Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"

class SecurityAgent:
    """
    Agent de sécurité fusionné avec modules security/
    - Vérifie JWT
    - Contrôle RBAC
    - Vérifie requêtes malveillantes
    - Limitation des requêtes
    - Route agents selon rôle
    """

    def __init__(self):
        # Services accessibles selon le rôle
        self.role_permissions = {
            UserRole.GUEST: ["classifier"],
            UserRole.USER: ["classifier", "search_engine", "iot_rag", "google_maps", "scraper"],
            UserRole.ADMIN: ["classifier", "search_engine", "iot_rag", "google_maps", "scraper", "technical_query"],
        }

    def check_jwt(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Vérifie le JWT via le module jwt_auth"""
        try:
            payload = jwt_auth.verify_jwt(token)
            return True, payload
        except Exception as e:
            return False, None

    def check_role(self, user_roles: List[str], required_role: str) -> bool:
        """Vérifie l'accès via le module rbac"""
        return rbac.check_access(user_roles, required_role)

    def check_request(self, request_content: str) -> bool:
        """Vérifie la requête via le module request_guard"""
        return not request_guard.analyze_request(request_content)

    def check_rate_limit(self, user_id: str) -> bool:
        """Vérifie le rate limiting via le module rate_limit"""
        return rate_limit.rate_limit(user_id)

    def get_allowed_agents(self, user_role: UserRole) -> List[str]:
        return self.role_permissions.get(user_role, [])

    def can_access_agent(self, user_role: UserRole, agent_name: str) -> bool:
        return agent_name in self.get_allowed_agents(user_role)

    def route_agent(self, token: str, query: str, requested_agent: str) -> str:
        """
        Point d'entrée unique pour exécuter un agent :
        - Vérifie JWT
        - Vérifie RBAC
        - Vérifie sécurité de la requête
        - Vérifie rate limit
        - Route vers l'agent
        """
        # 1️⃣ Vérification JWT
        valid_jwt, payload = self.check_jwt(token)
        if not valid_jwt:
            return "❌ Token invalide ou expiré"

        user_id = payload.get("sub")
        roles = payload.get("roles", [])
        
        # 2️⃣ Vérification RBAC
        if not self.check_role(roles, requested_agent):
            return "❌ Accès refusé : rôle insuffisant"

        # 3️⃣ Vérification requête
        if not self.check_request(query):
            return "❌ Contenu potentiellement malveillant détecté"

        # 4️⃣ Rate limiting
        if not self.check_rate_limit(user_id):
            return "❌ Trop de requêtes, ralentissez"

        # 5️⃣ Vérification si agent autorisé
        allowed_agents = []
        for role in roles:
            try:
                role_enum = UserRole(role)
                allowed_agents += self.get_allowed_agents(role_enum)
            except:
                continue

        if requested_agent not in allowed_agents:
            return "❌ Agent non autorisé pour ce rôle"

        # 6️⃣ Exécuter agent simulé
        return f"✅ Requête autorisée, agent '{requested_agent}' exécuté pour user {user_id} avec query '{query}'"
