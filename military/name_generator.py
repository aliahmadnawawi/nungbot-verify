"""Generator Data Veteran Militer US"""
import random
from datetime import datetime, timedelta

class NameGenerator:
    """Generator Nama US Standar"""
    
    ROOTS = {
        'prefixes': ['Al', 'Bar', 'Con', 'Dan', 'Ed', 'Frank', 'Greg', 'Har', 'Jeff', 'Ken', 
                    'Lar', 'Mike', 'Norm', 'Pat', 'Ron', 'Sam', 'Tim', 'Vic', 'Will'],
        'suffixes': ['son', 'man', 'ton', 'ley', 'ford', 'wood', 'berg', 'stein', 'field', 'brook']
    }
    
    LAST_NAMES = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 
        'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
        'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez',
        'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen',
        'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
        'Carter', 'Roberts'
    ]
    
    @classmethod
    def generate(cls):
        """Generate Nama Lengkap"""
        prefix = random.choice(cls.ROOTS['prefixes'])
        suffix = random.choice(cls.ROOTS['suffixes']) # Nama depan agak "bapak-bapak"
        
        # Kadang pakai nama simple, kadang compound
        if random.random() > 0.5:
            first_name = prefix + suffix
        else:
            first_name = random.choice(['James', 'Robert', 'John', 'Michael', 'David', 'William', 'Richard', 'Joseph', 'Thomas', 'Charles'])
            
        last_name = random.choice(cls.LAST_NAMES)
        
        return {
            'first_name': first_name.capitalize(),
            'last_name': last_name,
            'full_name': f"{first_name.capitalize()} {last_name}"
        }

def generate_email(first_name, last_name):
    """Email pribadi (Gmail/Yahoo/Outlook)"""
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    domain = random.choice(domains)
    num = random.randint(10, 999)
    return f"{first_name.lower()}{last_name.lower()}{num}@{domain}"

def generate_birth_date():
    """
    Tanggal Lahir Veteran (Usia 30-50 tahun)
    Range: 1975 - 1995
    """
    year = random.randint(1975, 1995)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    return f"{year}-{month}-{day}"

def generate_discharge_date(birth_date_str):
    """
    Tanggal Lepas Dinas (Discharge Date)
    Biasanya +20 sampai +30 tahun dari tahun lahir
    """
    birth_year = int(birth_date_str.split('-')[0])
    # Masuk militer umur 18, dinas 4 tahun = umur 22 keluar
    # Atau dinas lama sampai umur 40
    discharge_year = birth_year + random.randint(22, 35)
    
    # Jangan melebihi tahun sekarang
    current_year = datetime.now().year
    if discharge_year > current_year:
        discharge_year = current_year - 1
        
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    return f"{discharge_year}-{month}-{day}"