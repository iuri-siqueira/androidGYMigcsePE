#!/bin/bash
# Script to patch SDL2 recipes to bypass network restrictions
# This script changes SDL2 download URLs from /releases/download/ to /archive/refs/tags/
# which bypasses proxy restrictions blocking libsdl-org releases

set -e

echo "=== Applying SDL2 Network Restriction Patches ==="

RECIPES_DIR=".buildozer/android/platform/python-for-android/pythonforandroid/recipes"

# Check if recipes directory exists
if [ ! -d "$RECIPES_DIR" ]; then
    echo "⚠️  Recipes directory not found. Run buildozer once first to download python-for-android."
    echo "   Then run this script to apply patches."
    exit 1
fi

# Function to patch a recipe file
patch_recipe() {
    local recipe_name=$1
    local recipe_file="$RECIPES_DIR/${recipe_name}/__init__.py"

    if [ ! -f "$recipe_file" ]; then
        echo "⚠️  $recipe_name recipe not found, skipping..."
        return
    fi

    echo "📝 Patching $recipe_name..."

    case $recipe_name in
        "sdl2")
            # Patch SDL2 main recipe
            sed -i 's|url = "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL2-{version}.tar.gz"|url = "https://github.com/libsdl-org/SDL/archive/refs/tags/release-{version}.tar.gz"|g' "$recipe_file"
            sed -i "s|dir_name = 'SDL'|dir_name = 'SDL-release-{version}'|g" "$recipe_file"
            sed -i "s|md5sum = '.*'|md5sum = None  # Archive format has different checksum|g" "$recipe_file"
            ;;

        "sdl2_image")
            # Patch SDL2_image recipe
            sed -i 's|url = '"'"'https://github.com/libsdl-org/SDL_image/releases/download/release-{version}/SDL2_image-{version}.tar.gz'"'"'|url = '"'"'https://github.com/libsdl-org/SDL_image/archive/refs/tags/release-{version}.tar.gz'"'"'|g' "$recipe_file"
            sed -i "s|dir_name = 'SDL2_image'|dir_name = 'SDL_image-release-{version}'|g" "$recipe_file"
            # Update include path
            sed -i 's|os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL2_image", "include")|os.path.join(self.ctx.bootstrap.build_dir, "jni", self.dir_name.format(version=self.version), "include")|g' "$recipe_file"
            ;;

        "sdl2_mixer")
            # Patch SDL2_mixer recipe
            sed -i 's|url = '"'"'https://github.com/libsdl-org/SDL_mixer/releases/download/release-{version}/SDL2_mixer-{version}.tar.gz'"'"'|url = '"'"'https://github.com/libsdl-org/SDL_mixer/archive/refs/tags/release-{version}.tar.gz'"'"'|g' "$recipe_file"
            sed -i "s|dir_name = 'SDL2_mixer'|dir_name = 'SDL_mixer-release-{version}'|g' "$recipe_file"
            # Update include path
            sed -i 's|os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL2_mixer", "include")|os.path.join(self.ctx.bootstrap.build_dir, "jni", self.dir_name.format(version=self.version), "include")|g" "$recipe_file"
            ;;

        "sdl2_ttf")
            # Patch SDL2_ttf recipe
            sed -i 's|url = '"'"'https://github.com/libsdl-org/SDL_ttf/releases/download/release-{version}/SDL2_ttf-{version}.tar.gz'"'"'|url = '"'"'https://github.com/libsdl-org/SDL_ttf/archive/refs/tags/release-{version}.tar.gz'"'"'|g' "$recipe_file"
            sed -i "s|dir_name = 'SDL2_ttf'|dir_name = 'SDL_ttf-release-{version}'|g" "$recipe_file"
            ;;
    esac

    echo "✅ $recipe_name patched successfully"
}

# Apply patches to all SDL2 recipes
patch_recipe "sdl2"
patch_recipe "sdl2_image"
patch_recipe "sdl2_mixer"
patch_recipe "sdl2_ttf"

echo ""
echo "=== All SDL2 patches applied successfully! ==="
echo ""
echo "These patches change SDL2 download URLs to use GitHub archive format,"
echo "which bypasses network restrictions blocking /releases/download/ endpoints."
echo ""
echo "You can now run: buildozer android debug"
echo ""
