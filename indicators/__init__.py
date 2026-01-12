import os
import importlib
import streamlit as st

package_dir = os.path.dirname(__file__)
files = [f[:-3] for f in os.listdir(package_dir) if f.endswith('.py') and f != '__init__.py']

MODULLER = {}
for f in files:
    try:
        module = importlib.import_module(f'indicators.{f}')
        if hasattr(module, 'NAME'):
            MODULLER[module.NAME] = module
    except IndentationError as e:
        st.error(f"DİKKAT! '{f}.py' dosyasında boşluk hatası var. Lütfen bu dosyayı kontrol et.")
        # Hatayı detaylı görmek istersen: st.exception(e)
    except Exception as e:
        print(f"Hata {f}: {e}")
