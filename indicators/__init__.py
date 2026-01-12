import os
import importlib

# Klasör yolunu bul
package_dir = os.path.dirname(__file__)

# Klasördeki .py dosyalarını listele (__init__.py hariç)
files = [f[:-3] for f in os.listdir(package_dir) if f.endswith('.py') and f != '__init__.py']

# Tüm modülleri MODULLER sözlüğüne yükle
MODULLER = {}
for f in files:
    try:
        module = importlib.import_module(f'indicators.{f}')
        if hasattr(module, 'NAME'):
            MODULLER[module.NAME] = module
    except Exception as e:
        print(f"Modül yüklenemedi {f}: {e}")
