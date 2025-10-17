import os
import re
import sys


def add_module_to_settings(module_name):
    """
    Busca un archivo settings.gradle o settings.gradle.kts y agrega el nuevo módulo
    en orden alfabético.
    """
    settings_file_path = None

    # Busca el archivo de settings en el directorio actual
    if os.path.exists('settings.gradle.kts'):
        settings_file_path = 'settings.gradle.kts'
    elif os.path.exists('settings.gradle'):
        settings_file_path = 'settings.gradle'

    if not settings_file_path:
        print("\nAdvertencia: No se encontró 'settings.gradle.kts' o 'settings.gradle'.")
        print(f"Por favor, agrega manualmente 'include(\":{module_name}\")' a tu archivo de settings.")
        return

    try:
        with open(settings_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        is_kts = settings_file_path.endswith('.kts')
        new_module_entry = module_name

        modules = set()
        other_lines = []

        # Extraer módulos existentes y separar las otras líneas
        for line in lines:
            # Verifica si la línea comienza con 'include' (ignorando espacios)
            if line.strip().startswith('include('):
                # Busca patrones como (":module:submodule") o ("module") y captura solo el nombre
                found = re.findall(r"['\"]:?([\w.:-]+)['\"]", line)
                if found:
                    for mod in found:
                        modules.add(mod)
            else:
                other_lines.append(line.rstrip())

        # Agregar el nuevo módulo
        modules.add(new_module_entry)

        # Ordenar alfabéticamente
        sorted_modules = sorted(list(modules))

        # Reconstruir el archivo
        with open(settings_file_path, 'w', encoding='utf-8') as f:
            # Escribir las líneas que no son 'include'
            if other_lines:
                f.write("\n".join(other_lines))
                f.write("\n")

            # Crear una lista de las declaraciones de include con el formato correcto
            include_statements = []
            for mod in sorted_modules:
                include_statements.append(f'include("{mod}")')

            # Unir las declaraciones con saltos de línea y escribir al archivo.
            # Esto evita un salto de línea extra al final.
            f.write("\n".join(include_statements))

        print(f"\n¡Módulo '{module_name}' agregado exitosamente a '{settings_file_path}'!")

    except Exception as e:
        print(f"\nOcurrió un error al modificar '{settings_file_path}': {e}")
        print(f"Por favor, agrega manualmente 'include(\":{module_name}\")' a tu archivo.")


def create_android_library_structure(feature_name):
    """
    Crea la estructura de directorios y archivos para una librería de Android
    en el directorio actual, con contenido por defecto para algunos archivos.

    Args:
        feature_name (str): El nombre del directorio raíz para la librería (ej: 'consumer-credit').
                           Los guiones y espacios se eliminarán para el nombre del paquete.
    """
    root_dir = feature_name

    if os.path.exists(root_dir):
        print(f"El directorio '{root_dir}' ya existe en la ubicación actual. Por favor, elige otro nombre.")
        return

    # Convierte el nombre de la librería en un nombre de paquete válido (sin guiones ni espacios)
    package_name = feature_name.replace('-', '').replace(' ', '')
    full_namespace = f'cl.bci.sismo.mach.{package_name}'

    print(f"Creando la librería '{root_dir}'...")
    print(f"El namespace del paquete será: '{full_namespace}'")

    # Contenido por defecto para los archivos
    android_manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

</manifest>
"""

    gitignore_content = "/build\n"

    build_gradle_kts_content = f"""plugins {{
    id("com.android.library")
    id("kotlin-android")
    id("com.google.devtools.ksp")
    id("dagger.hilt.android.plugin")
    id("de.mannodermaus.android-junit5")
    id("androidx.navigation.safeargs")
    id("org.jetbrains.kotlin.plugin.compose")
    id("cl.bci.sismo.android.base")
    id("cl.bci.sismo.android.kotlin.version")
    id("cl.bci.sismo.android.build.types")
}}

apply(from = "$rootDir/jacoco.gradle")

android {{
    namespace = "{full_namespace}"

    buildFeatures {{
        viewBinding = false
        compose = true
        dataBinding = false
    }}

    defaultConfig {{
        vectorDrawables {{
            useSupportLibrary = true
        }}
    }}
}}

dependencies {{
    ksp(libs.hilt.android.compiler)

    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.activity)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.compose.material)
    implementation(libs.compose.material3)
    implementation(libs.compose.navigation)
    implementation(libs.compose.hilt.navigation)
    implementation(libs.compose.ui.tooling)
    implementation(libs.compose.ui.test.manifest)
    implementation(libs.compose.lottie)
    implementation(libs.compose.coil)
    implementation(libs.kotlin.stdlib)
    implementation(libs.timber)
    implementation(libs.retrofit)
    implementation(libs.retrofit.gson)
    implementation(libs.core.ktx)

    implementation(libs.fragment)
    implementation(libs.activity)
    implementation(libs.navigation.ui)
    implementation(libs.hilt.android)
    implementation(libs.material)
    implementation(libs.gson)


    implementation(project(":mach-foundation:util"))
    implementation(project(":view"))
    implementation(project(":pin"))
    implementation(project(":mach-essential:analytics"))
    implementation(project(":mach-essential:analytics:core"))
    implementation(project(":deeplink-navigation"))
    implementation(project(":customer-service:help-center"))
    implementation(project(":mach-legacy-arch:core"))
    implementation(project(":mach-legacy-arch:core-legacy"))

    testRuntimeOnly(libs.junit.jupiter.engine)
    testImplementation(libs.coroutines.testing)
    testImplementation(libs.junit.api)
    testImplementation(libs.mockk)
    testImplementation(libs.junit.params)
}}
"""

    # Diccionario de archivos a crear con su contenido
    files_to_create = {
        "consumer-rules.pro": "",
        "proguard-rules.pro": "",
        ".gitignore": gitignore_content,
        "build.gradle.kts": build_gradle_kts_content,
        "src/main/AndroidManifest.xml": android_manifest_content,
    }

    # Lista de directorios a crear
    dirs_to_create = [
        f"src/main/java/cl/bci/sismo/mach/{package_name}/data",
        f"src/main/java/cl/bci/sismo/mach/{package_name}/domain",
        f"src/main/java/cl/bci/sismo/mach/{package_name}/presentation",
        f"src/main/java/cl/bci/sismo/mach/{package_name}/di",
        f"src/test/java/cl/bci/sismo/mach/{package_name}/data",
        f"src/test/java/cl/bci/sismo/mach/{package_name}/domain",
        f"src/test/java/cl/bci/sismo/mach/{package_name}/presentation",
    ]

    try:
        # Crear los directorios principales
        for dir_path in dirs_to_create:
            full_path = os.path.join(root_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)

        # Crear los archivos con su contenido
        for file_path, content in files_to_create.items():
            full_path = os.path.join(root_dir, file_path)

            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"\n¡Estructura de la librería creada exitosamente en la carpeta '{root_dir}'!")

        # Agregar el nuevo módulo al archivo settings
        add_module_to_settings(feature_name)

    except OSError as e:
        print(f"\nError al crear la estructura: {e}")


if __name__ == "__main__":
    library_name = ""
    # Comprobar si se pasó un nombre de librería como argumento de línea de comandos
    if len(sys.argv) > 1:
        library_name = sys.argv[1]
    else:
        # Si no, volver al modo interactivo
        library_name = input("Introduce el nombre para tu nueva librería (ej: consumer-credit): ")

    if library_name:
        create_android_library_structure(library_name)
    else:
        print("El nombre de la librería no puede estar vacío. Uso: python create_android_library.py <nombre-de-libreria>")

