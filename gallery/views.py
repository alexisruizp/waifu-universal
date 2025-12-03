from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings
import re
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.cache import cache_page

def parse_waifu_info():
    info_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
    waifu_info = {}
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            content = f.read()
        sections = re.split(r'###\s+', content)[1:]  # Split by ### and skip empty first
        for section in sections:
            lines = section.strip().split('\n')
            name = lines[0].strip()
            info = '\n'.join(lines[1:]).strip()
            key = name.split(' (')[0].lower() if ' (' in name else name.lower()
            waifu_info[key] = {'info': info.replace('**', ''), 'category': extract_category(info)}
            if '(' in name and ')' in name:
                alt_key = name.split('(')[1].split(')')[0].strip().lower()
                waifu_info[alt_key] = {'info': info.replace('**', ''), 'category': extract_category(info)}
    return waifu_info

def extract_category(info):
    # Extraer categoría del texto de info
    if 'Genshin Impact' in info:
        return 'Genshin Impact'
    elif 'Wuthering Waves' in info:
        return 'Wuthering Waves'
    elif 'Zenless Zone Zero' in info:
        return 'Zenless Zone Zero'
    elif 'Honkai: Star Rail' in info:
        return 'Honkai: Star Rail'
    elif 'Hazbin Hotel' in info:
        return 'Hazbin Hotel'
    elif 'League of Legends' in info:
        return 'League of Legends'
    elif 'Resident Evil' in info:
        return 'Resident Evil'
    else:
        return 'Otros'

@cache_page(60*15)
def waifus_gallery(request):
    # Ajusta la ruta a tu carpeta 'waifus'
    waifus_root = os.path.join(settings.BASE_DIR, 'waifus')
    waifu_info = parse_waifu_info()
    waifus = []
    featured_waifu = None
    query = request.GET.get('q', '').strip().lower()
    category_filter = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', 'name')

    # Leer waifu destacada desde un archivo
    featured_file = os.path.join(settings.BASE_DIR, 'featured_waifu.txt')
    if os.path.exists(featured_file):
        with open(featured_file, 'r', encoding='utf-8') as f:
            featured_name = f.read().strip()
            if featured_name:
                featured_folder = featured_name.lower().replace(' ', '_')
                featured_path = os.path.join(waifus_root, featured_folder)
                if os.path.isdir(featured_path):
                    images = [f for f in os.listdir(featured_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                    if images:
                        key = featured_folder.lower()
                        # Try multiple keys for info lookup
                        info_data = waifu_info.get(key, {})
                        description = info_data.get('info', '') if isinstance(info_data, dict) else info_data
                        category = info_data.get('category', 'Otros') if isinstance(info_data, dict) else 'Otros'
                        if not description:
                            # Try without spaces/underscores
                            key_normalized = key.replace(' ', '').replace('_', '')
                            for info_key in waifu_info:
                                if info_key.replace(' ', '').replace('_', '') == key_normalized:
                                    info_data = waifu_info[info_key]
                                    description = info_data.get('info', '') if isinstance(info_data, dict) else info_data
                                    category = info_data.get('category', 'Otros') if isinstance(info_data, dict) else 'Otros'
                                    break
                        if not description:
                            description = f'Descripción de {featured_name}.'
                        info = description
                        featured_waifu = {
                            'name': featured_name,
                            'folder': featured_folder,
                            'image': os.path.join('waifus', featured_folder, images[0]),
                            'description': description[:300] + '...' if len(description) > 300 else description,
                            'info': info,
                            'category': category
                        }

    for folder in os.listdir(waifus_root):
        folder_path = os.path.join(waifus_root, folder)
        if os.path.isdir(folder_path):
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if images:
                name = folder.replace('_', ' ').title()
                key = folder.lower()
                # Try multiple keys for info lookup
                info_data = waifu_info.get(key, {})
                description = info_data.get('info', '') if isinstance(info_data, dict) else info_data
                category = info_data.get('category', 'Otros') if isinstance(info_data, dict) else 'Otros'
                if not description:
                    # Try without spaces/underscores
                    key_normalized = key.replace(' ', '').replace('_', '')
                    for info_key in waifu_info:
                        if info_key.replace(' ', '').replace('_', '') == key_normalized:
                            info_data = waifu_info[info_key]
                            description = info_data.get('info', '') if isinstance(info_data, dict) else info_data
                            category = info_data.get('category', 'Otros') if isinstance(info_data, dict) else 'Otros'
                            break
                if not description:
                    description = f'Descripción de {folder}. Origen: Gacha.'
                waifu_data = {
                    'name': name,
                    'folder': folder,
                    'image': os.path.join('waifus', folder, images[0]),  # Ruta relativa para media
                    'description': description[:200] + '...' if len(description) > 200 else description,  # Shorten for main page
                    'category': category
                }
                # Filtrar por búsqueda y categoría
                include = True
                if query:
                    if not (query in name.lower() or query in folder.lower() or query in description.lower()):
                        include = False
                if category_filter and category_filter != 'all':
                    if category.lower() != category_filter.lower():
                        include = False
                if include:
                    waifus.append(waifu_data)
    # Ordenar waifus
    if sort == 'name':
        waifus.sort(key=lambda x: x['name'])
    elif sort == 'category':
        waifus.sort(key=lambda x: x['category'])
    # Default is name
    # Estadísticas
    categories = set([w['category'] for w in waifus])
    category_count = len(categories)
    images_count = sum(len([f for f in os.listdir(os.path.join(waifus_root, f)) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]) for f in os.listdir(waifus_root) if os.path.isdir(os.path.join(waifus_root, f)))
    paginator = Paginator(waifus, 12)  # 12 waifus por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gallery/index.html', {'page_obj': page_obj, 'featured_waifu': featured_waifu, 'query': query, 'category_filter': category_filter, 'sort': sort, 'category_count': category_count, 'images_count': images_count})

def waifu_detail(request, name):
    waifus_root = os.path.join(settings.BASE_DIR, 'waifus')
    waifu_info = parse_waifu_info()
    name_normalized = name.lower().replace(' ', '').replace('_', '')

    folder_path = None
    folder = None
    for f in os.listdir(waifus_root):
        if os.path.isdir(os.path.join(waifus_root, f)):
            folder_normalized = f.lower().replace(' ', '').replace('_', '')
            if folder_normalized == name_normalized:
                folder_path = os.path.join(waifus_root, f)
                folder = f
                break

    if folder_path:
        images = [os.path.join('waifus', folder, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        info_data = waifu_info.get(name.lower(), 'Información no disponible.')
        info = info_data.get('info', 'Información no disponible.') if isinstance(info_data, dict) else info_data
        return render(request, 'gallery/waifu_detail.html', {
            'name': name,
            'images': images,
            'info': info
        })
    return render(request, 'gallery/waifu_not_found.html', {'name': name})

def portfolio(request):
    # Same as gallery
    return waifus_gallery(request)

def info(request):
    info_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')  # O text/markdown si es md
    return HttpResponse("Información no encontrada.")

def add_waifu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')
        set_featured = request.POST.get('set_featured') == 'on'

        if not name or not category or not description or len(images) < 4:
            messages.error(request, 'Nombre, categoría, descripción y al menos 4 imágenes son obligatorios.')
            return redirect('add_waifu')

        # Prepend category to description for extraction
        full_description = f'{category}\n\n{description}'

        # Crear carpeta para la waifu
        waifu_folder = os.path.join(settings.BASE_DIR, 'waifus', name.lower().replace(' ', '_'))
        os.makedirs(waifu_folder, exist_ok=True)

        # Guardar imágenes
        for image in images:
            image_path = os.path.join(waifu_folder, image.name)
            with open(image_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)

        # Actualizar archivo de información
        info_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
        with open(info_path, 'a', encoding='utf-8') as f:
            f.write(f'\n### {name}\n{full_description}\n')

        # Establecer como waifu destacada automáticamente (siempre la última añadida)
        featured_file = os.path.join(settings.BASE_DIR, 'featured_waifu.txt')
        with open(featured_file, 'w', encoding='utf-8') as f:
            f.write(name)

        if set_featured:
            messages.success(request, f'Waifu {name} añadida exitosamente y establecida como waifu de temporada! 🌟')
        else:
            messages.success(request, f'Waifu {name} añadida exitosamente y ahora es la waifu de temporada! 🌟')
        return redirect('waifus_gallery')

    return render(request, 'gallery/add_waifu.html')

def edit_waifu(request, name):
    waifus_root = os.path.join(settings.BASE_DIR, 'waifus')
    waifu_info = parse_waifu_info()
    name_normalized = name.lower().replace(' ', '').replace('_', '')

    folder_path = None
    folder = None
    for f in os.listdir(waifus_root):
        if os.path.isdir(os.path.join(waifus_root, f)):
            folder_normalized = f.lower().replace(' ', '').replace('_', '')
            if folder_normalized == name_normalized:
                folder_path = os.path.join(waifus_root, f)
                folder = f
                break

    if not folder_path:
        return HttpResponse("Waifu no encontrada.")

    if request.method == 'POST':
        # Verificar si se solicita eliminar la waifu completa
        if request.POST.get('delete_waifu') == 'true':
            # Eliminar carpeta completa
            import shutil
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            # Eliminar entrada del archivo de información
            info_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                sections = re.split(r'###\s+', content)[1:]
                updated_sections = []
                for section in sections:
                    lines = section.strip().split('\n')
                    section_name = lines[0].strip()
                    if section_name.lower() != name.lower():
                        updated_sections.append(f'### {section}')
                new_content = '\n\n'.join(updated_sections)
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            messages.success(request, f'Waifu {name} eliminada completamente del sistema. 💀')
            return redirect('waifus_gallery')

        new_name = request.POST.get('name')
        description = request.POST.get('description').replace('**', '')
        new_images = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')

        # Actualizar nombre si cambió
        if new_name and new_name != name:
            new_folder = os.path.join(waifus_root, new_name.lower().replace(' ', '_'))
            os.rename(folder_path, new_folder)
            folder_path = new_folder
            folder = new_name.lower().replace(' ', '_')
            name = new_name

        # Eliminar imágenes seleccionadas
        if delete_images:
            for filename in delete_images:
                image_path = os.path.join(folder_path, filename)
                if os.path.exists(image_path):
                    os.remove(image_path)

        # Actualizar descripción
        info_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Actualizar la sección correspondiente
            sections = re.split(r'###\s+', content)[1:]
            updated_sections = []
            for section in sections:
                lines = section.strip().split('\n')
                section_name = lines[0].strip()
                if section_name.lower() == name.lower():
                    updated_sections.append(f'### {name}\n{description}')
                else:
                    updated_sections.append(f'### {section}')
            new_content = '\n\n'.join(updated_sections)
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        # Añadir nuevas imágenes si se subieron
        if new_images:
            for image in new_images:
                image_path = os.path.join(folder_path, image.name)
                with open(image_path, 'wb+') as f:
                    for chunk in image.chunks():
                        f.write(chunk)

        messages.success(request, f'Waifu {name} actualizada exitosamente.')
        return redirect('waifu_detail', name=name)

    # Para GET, mostrar formulario con datos actuales
    images = [{'path': os.path.join('waifus', folder, f), 'filename': f} for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    info_data = waifu_info.get(folder, {})
    info = info_data.get('info', '') if isinstance(info_data, dict) else info_data
    return render(request, 'gallery/edit_waifu.html', {
        'name': name,
        'images': images,
        'info': info
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('waifus_gallery')
    else:
        form = UserCreationForm()
    return render(request, 'gallery/register.html', {'form': form})

def backup(request):
    file_path = os.path.join(settings.BASE_DIR, 'informacion de las waifus.txt')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='backup_waifus.txt')
    return HttpResponse("Backup no disponible.")
