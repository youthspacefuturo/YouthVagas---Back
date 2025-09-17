import re

class PhoneValidator:
    """Validador de números de telefone brasileiros"""
    
    @staticmethod
    def validate_phone(phone):
        """
        Validar número de telefone brasileiro
        
        Args:
            phone: Número de telefone
            
        Returns:
            bool: True se válido, False caso contrário
        """
        if not phone:
            return False
        
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'\D', '', phone)
        
        # Validar formatos brasileiros
        # 11 dígitos: (11) 99999-9999
        # 10 dígitos: (11) 9999-9999
        if len(clean_phone) == 11:
            # Celular com 9 na frente
            return clean_phone[2] == '9' and clean_phone[:2] in ['11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28', '31', '32', '33', '34', '35', '37', '38', '41', '42', '43', '44', '45', '46', '47', '48', '49', '51', '53', '54', '55', '61', '62', '63', '64', '65', '66', '67', '68', '69', '71', '73', '74', '75', '77', '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '91', '92', '93', '94', '95', '96', '97', '98', '99']
        elif len(clean_phone) == 10:
            # Telefone fixo
            return clean_phone[:2] in ['11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28', '31', '32', '33', '34', '35', '37', '38', '41', '42', '43', '44', '45', '46', '47', '48', '49', '51', '53', '54', '55', '61', '62', '63', '64', '65', '66', '67', '68', '69', '71', '73', '74', '75', '77', '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '91', '92', '93', '94', '95', '96', '97', '98', '99']
        
        return False
    
    @staticmethod
    def format_phone(phone):
        """
        Formatar número de telefone
        
        Args:
            phone: Número de telefone
            
        Returns:
            str: Número formatado
        """
        if not phone:
            return ""
        
        clean_phone = re.sub(r'\D', '', phone)
        
        if len(clean_phone) == 11:
            return f"({clean_phone[:2]}) {clean_phone[2:7]}-{clean_phone[7:]}"
        elif len(clean_phone) == 10:
            return f"({clean_phone[:2]}) {clean_phone[2:6]}-{clean_phone[6:]}"
        
        return phone
