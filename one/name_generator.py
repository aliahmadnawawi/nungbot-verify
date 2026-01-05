"""Generator Nama Acak"""
import random


class NameGenerator:
    """Generator Nama Inggris (English Name Generator)"""
    
    # Komponen Suku Kata (JANGAN DIUBAH agar nama terdengar alami)
    ROOTS = {
        'prefixes': ['Al', 'Bri', 'Car', 'Dan', 'El', 'Fer', 'Gar', 'Har', 'Jes', 'Kar', 
                    'Lar', 'Mar', 'Nor', 'Par', 'Quin', 'Ros', 'Sar', 'Tar', 'Val', 'Wil'],
        'middles': ['an', 'en', 'in', 'on', 'ar', 'er', 'or', 'ur', 'al', 'el', 
                   'il', 'ol', 'am', 'em', 'im', 'om', 'ay', 'ey', 'oy', 'ian'],
        'suffixes': ['ton', 'son', 'man', 'ley', 'field', 'ford', 'wood', 'stone', 'worth', 'berg',
                    'stein', 'bach', 'heim', 'gard', 'land', 'wick', 'shire', 'dale', 'brook', 'ridge'],
        'name_roots': ['Alex', 'Bern', 'Crist', 'Dav', 'Edw', 'Fred', 'Greg', 'Henr', 'Ivan', 'John',
                      'Ken', 'Leon', 'Mich', 'Nick', 'Oliv', 'Paul', 'Rich', 'Step', 'Thom', 'Will'],
        'name_endings': ['a', 'e', 'i', 'o', 'y', 'ie', 'ey', 'an', 'en', 'in', 
                        'on', 'er', 'ar', 'or', 'el', 'al', 'iel', 'ael', 'ine', 'lyn']
    }
    
    # Pola penyusunan nama Depan dan Belakang
    PATTERNS = {
        'first_name': [
            ['prefix', 'ending'],
            ['name_root', 'ending'],
            ['prefix', 'middle', 'ending'],
            ['name_root', 'middle', 'ending']
        ],
        'last_name': [
            ['prefix', 'suffix'],
            ['name_root', 'suffix'],
            ['prefix', 'middle', 'suffix'],
            ['compound']
        ]
    }
    
    @classmethod
    def _generate_component(cls, pattern):
        """Membuat komponen nama berdasarkan pola"""
        components = []
        for part in pattern:
            if part == 'prefix':
                component = random.choice(cls.ROOTS['prefixes'])
            elif part == 'middle':
                component = random.choice(cls.ROOTS['middles'])
            elif part == 'suffix':
                component = random.choice(cls.ROOTS['suffixes'])
            elif part == 'name_root':
                component = random.choice(cls.ROOTS['name_roots'])
            elif part == 'ending':
                component = random.choice(cls.ROOTS['name_endings'])
            elif part == 'compound':
                part1 = random.choice(cls.ROOTS['prefixes'])
                part2 = random.choice(cls.ROOTS['suffixes'])
                component = part1 + part2
            else:
                component = ''
            
            components.append(component)
        
        return ''.join(components)
    
    @classmethod
    def _format_name(cls, name):
        """Format nama (Huruf pertama kapital)"""
        return name.capitalize()
    
    @classmethod
    def generate(cls):
        """
        Membuat nama Inggris acak
        
        Returns:
            dict: berisi first_name, last_name, full_name
        """
        first_name_pattern = random.choice(cls.PATTERNS['first_name'])
        last_name_pattern = random.choice(cls.PATTERNS['last_name'])
        
        first_name = cls._generate_component(first_name_pattern)
        last_name = cls._generate_component(last_name_pattern)
        
        return {
            'first_name': cls._format_name(first_name),
            'last_name': cls._format_name(last_name),
            'full_name': f"{cls._format_name(first_name)} {cls._format_name(last_name)}"
        }


def generate_email(school_domain='psu.edu'):
    """
    Membuat email kampus acak
    
    Args:
        school_domain: Domain kampus (default psu.edu)
    
    Returns:
        str: Alamat email
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    username = ''.join(random.choice(chars) for _ in range(8))
    return f"{username}@{school_domain}"


def generate_birth_date():
    """
    Membuat tanggal lahir acak (Tahun 2000-2005)
    Cocok untuk usia mahasiswa S1 saat ini.
    
    Returns:
        str: Format YYYY-MM-DD
    """
    year = 2000 + random.randint(0, 5)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    return f"{year}-{month}-{day}"