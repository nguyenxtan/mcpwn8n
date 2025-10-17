"""
Natural Language Parser for user queries
Parses Vietnamese and English natural language to extract intent
"""
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedIntent:
    """Parsed user intent"""
    check_health: bool = False
    check_users: bool = False
    check_services: bool = False
    check_logs: bool = False
    check_metrics: bool = False
    log_timeframe: str = "1h"
    log_level: Optional[str] = None
    log_service: Optional[str] = None
    log_search: Optional[str] = None
    confidence: float = 0.0
    original_query: str = ""


class NLPParser:
    """
    Natural Language Parser for system check queries
    Supports both Vietnamese and English
    """

    def __init__(self):
        # Define patterns for different intents
        self.patterns = {
            "health": [
                # Vietnamese patterns
                r"(kiểm tra|check).*(hệ thống|system|health|sức khỏe)",
                r"(health|sức khỏe).*(hệ thống|system)",
                r"(status|trạng thái).*(hệ thống|system)",
                r"hệ thống.*(hoạt động|running|ok)",

                # English patterns
                r"(check|verify).*(system|health)",
                r"(system|server).*(health|status)",
                r"is.*(system|server).*(up|running|healthy)",
            ],

            "users": [
                # Vietnamese patterns
                r"(người dùng|user).*(status|trạng thái|đang|online)",
                r"(kiểm tra|check).*(user|người dùng|account|tài khoản)",
                r"(ai|who).*(đang|currently).*(online|active)",
                r"số lượng.*(user|người dùng)",

                # English patterns
                r"(user|users).*(status|active|online)",
                r"(check|list).*(user|users|account)",
                r"who.*(online|active|logged in)",
                r"(how many|count).*(user|users)",
            ],

            "services": [
                # Vietnamese patterns
                r"(dịch vụ|service).*(nào|list|danh sách)",
                r"(kiểm tra|check).*(service|dịch vụ|api)",
                r"các.*(service|dịch vụ).*(đang chạy|running)",
                r"danh sách.*(service|dịch vụ)",

                # English patterns
                r"(service|services).*(list|available|running)",
                r"(check|list).*(service|services|api)",
                r"what.*(service|services).*(running|available)",
                r"(show|get).*(service|services)",
            ],

            "logs": [
                # Vietnamese patterns
                r"(log|nhật ký|lịch sử).*(gần đây|recent|latest)",
                r"(kiểm tra|check|xem).*(log|nhật ký)",
                r"(error|lỗi).*(log|nhật ký)",
                r"(tìm|search).*(log|nhật ký)",

                # English patterns
                r"(log|logs).*(recent|latest|last)",
                r"(check|view|show).*(log|logs)",
                r"(error|warning).*(log|logs)",
                r"(search|find).*(log|logs)",
            ],

            "metrics": [
                # Vietnamese patterns
                r"(metric|chỉ số|số liệu).*(hiện tại|current|now)",
                r"(hiệu suất|performance).*(hệ thống|system)",
                r"(cpu|memory|ram|disk).*(usage|sử dụng)",
                r"(kiểm tra|check).*(metric|chỉ số|performance)",

                # English patterns
                r"(metric|metrics).*(current|now|latest)",
                r"(system|server).*(performance|metric)",
                r"(cpu|memory|disk|network).*(usage|utilization)",
                r"(check|show).*(metric|metrics|performance)",
            ],

            "all": [
                # Vietnamese patterns
                r"(kiểm tra|check).*(toàn bộ|tất cả|all|everything)",
                r"(toàn bộ|tất cả).*(hệ thống|system)",
                r"(overview|tổng quan).*(hệ thống|system)",
                r"full.*(check|scan)",

                # English patterns
                r"(check|scan).*(all|everything|full)",
                r"(full|complete).*(system|check|scan)",
                r"(system|server).*(overview|summary)",
                r"everything",
            ]
        }

        # Timeframe patterns
        self.timeframe_patterns = {
            r"(\d+)\s*(phút|minute|min)": lambda m: f"{m.group(1)}m",
            r"(\d+)\s*(giờ|hour|h)": lambda m: f"{m.group(1)}h",
            r"(\d+)\s*(ngày|day|d)": lambda m: f"{m.group(1)}d",
            r"1\s*(tuần|week|w)": lambda m: "7d",
            r"hôm nay|today": lambda m: "24h",
            r"gần đây|recent|latest": lambda m: "1h",
        }

        # Log level patterns
        self.log_level_patterns = {
            r"(error|lỗi)": "error",
            r"(warning|cảnh báo)": "warning",
            r"(info|thông tin)": "info",
            r"(debug)": "debug",
            r"(critical|nghiêm trọng)": "critical",
        }

    def parse(self, query: str) -> ParsedIntent:
        """
        Parse natural language query to extract intent

        Args:
            query: User query in Vietnamese or English

        Returns:
            ParsedIntent object
        """
        query_lower = query.lower().strip()
        intent = ParsedIntent(original_query=query)

        logger.debug(f"Parsing query: {query}")

        # Check for "all" pattern first (highest priority)
        if self._match_patterns(query_lower, self.patterns["all"]):
            intent.check_health = True
            intent.check_users = True
            intent.check_services = True
            intent.check_logs = True
            intent.check_metrics = True
            intent.confidence = 0.95
            logger.info("Detected 'all systems' intent")
            return intent

        # Check individual patterns
        matches = 0

        if self._match_patterns(query_lower, self.patterns["health"]):
            intent.check_health = True
            matches += 1

        if self._match_patterns(query_lower, self.patterns["users"]):
            intent.check_users = True
            matches += 1

        if self._match_patterns(query_lower, self.patterns["services"]):
            intent.check_services = True
            matches += 1

        if self._match_patterns(query_lower, self.patterns["logs"]):
            intent.check_logs = True
            matches += 1

        if self._match_patterns(query_lower, self.patterns["metrics"]):
            intent.check_metrics = True
            matches += 1

        # If no specific match, default to health check
        if matches == 0:
            logger.warning(f"No pattern matched, defaulting to health check")
            intent.check_health = True
            intent.confidence = 0.3
        else:
            intent.confidence = min(0.9, 0.5 + (matches * 0.15))

        # Parse log-specific parameters if logs are requested
        if intent.check_logs:
            intent.log_timeframe = self._parse_timeframe(query_lower)
            intent.log_level = self._parse_log_level(query_lower)
            intent.log_service = self._parse_service_name(query_lower)
            intent.log_search = self._parse_search_term(query_lower)

        logger.info(f"Parsed intent: {intent} (confidence: {intent.confidence:.2f})")
        return intent

    def _match_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern in the list"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _parse_timeframe(self, text: str) -> str:
        """Extract timeframe from text"""
        for pattern, converter in self.timeframe_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                timeframe = converter(match)
                logger.debug(f"Detected timeframe: {timeframe}")
                return timeframe
        return "1h"  # default

    def _parse_log_level(self, text: str) -> Optional[str]:
        """Extract log level from text"""
        for pattern, level in self.log_level_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Detected log level: {level}")
                return level
        return None

    def _parse_service_name(self, text: str) -> Optional[str]:
        """Extract service name from text"""
        # Look for patterns like "service=xxx" or "from xxx service"
        patterns = [
            r"service[=:\s]+([a-zA-Z0-9_-]+)",
            r"from\s+([a-zA-Z0-9_-]+)\s+service",
            r"của\s+([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                service = match.group(1)
                logger.debug(f"Detected service: {service}")
                return service
        return None

    def _parse_search_term(self, text: str) -> Optional[str]:
        """Extract search term from text"""
        # Look for patterns like "search for xxx" or "tìm xxx"
        patterns = [
            r"search\s+(?:for\s+)?['\"]?([^'\"]+)['\"]?",
            r"tìm\s+['\"]?([^'\"]+)['\"]?",
            r"find\s+['\"]?([^'\"]+)['\"]?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                search_term = match.group(1).strip()
                logger.debug(f"Detected search term: {search_term}")
                return search_term
        return None

    def to_api_params(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Convert parsed intent to API call parameters

        Args:
            intent: Parsed intent

        Returns:
            Dictionary of parameters for ABCSystemClient
        """
        params = {
            "include_health": intent.check_health,
            "include_users": intent.check_users,
            "include_services": intent.check_services,
            "include_logs": intent.check_logs,
            "include_metrics": intent.check_metrics,
        }

        # Add log query parameters if logs are requested
        if intent.check_logs:
            log_params = {
                "timeframe": intent.log_timeframe,
                "limit": 100
            }
            if intent.log_level:
                log_params["level"] = intent.log_level
            if intent.log_service:
                log_params["service"] = intent.log_service
            if intent.log_search:
                log_params["search"] = intent.log_search

            params["log_params"] = log_params

        return params
