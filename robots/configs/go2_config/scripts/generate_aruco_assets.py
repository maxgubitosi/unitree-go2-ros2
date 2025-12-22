#!/usr/bin/env python3
"""
Genera los assets del marcador ArUco para Gazebo Classic 11.
- Imagen PNG del marcador ArUco
- Mesh COLLADA (.dae) con textura relativa

Uso:
    python3 generate_aruco_assets.py --output ../models/aruco_marker --id 23 --size 0.2
"""

import os
import argparse


def generate_aruco_png(output_dir: str, marker_id: int = 23, pixels: int = 200) -> str:
    """Genera imagen PNG del marcador ArUco usando OpenCV."""
    try:
        import cv2
        import numpy as np
        from cv2 import aruco
    except ImportError:
        print("ERROR: OpenCV no instalado. Ejecuta: pip install opencv-contrib-python")
        return None

    # Diccionario ArUco 4x4 (50 marcadores)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    # Generar el marcador
    marker_image = aruco.generateImageMarker(aruco_dict, marker_id, pixels)
    
    # Agregar borde blanco (requerido para detección)
    border_size = pixels // 8
    marker_with_border = cv2.copyMakeBorder(
        marker_image,
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT,
        value=255
    )
    
    # Guardar
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"aruco_{marker_id}.png")
    cv2.imwrite(png_path, marker_with_border)
    print(f"✓ Generado: {png_path}")
    return png_path


def generate_aruco_dae(output_dir: str, marker_id: int = 23, size: float = 0.2) -> str:
    """Genera mesh COLLADA con referencia a textura en mismo directorio."""
    
    texture_filename = f"aruco_{marker_id}.png"
    dae_filename = f"aruco_{marker_id}.dae"
    
    half = size / 2.0
    
    dae_content = f'''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset>
    <created>2025-01-01T00:00:00</created>
    <modified>2025-01-01T00:00:00</modified>
    <unit name="meter" meter="1"/>
    <up_axis>Z_UP</up_axis>
  </asset>
  <library_images>
    <image id="aruco_image" name="aruco_image">
      <init_from>{texture_filename}</init_from>
    </image>
  </library_images>
  <library_effects>
    <effect id="aruco_effect">
      <profile_COMMON>
        <newparam sid="aruco_surface">
          <surface type="2D">
            <init_from>aruco_image</init_from>
          </surface>
        </newparam>
        <newparam sid="aruco_sampler">
          <sampler2D>
            <source>aruco_surface</source>
            <minfilter>LINEAR</minfilter>
            <magfilter>LINEAR</magfilter>
          </sampler2D>
        </newparam>
        <technique sid="common">
          <lambert>
            <emission><color>0 0 0 1</color></emission>
            <ambient><color>1 1 1 1</color></ambient>
            <diffuse>
              <texture texture="aruco_sampler" texcoord="UVMap"/>
            </diffuse>
          </lambert>
        </technique>
      </profile_COMMON>
    </effect>
  </library_effects>
  <library_materials>
    <material id="aruco_material" name="aruco_material">
      <instance_effect url="#aruco_effect"/>
    </material>
  </library_materials>
  <library_geometries>
    <geometry id="aruco_plane" name="aruco_plane">
      <mesh>
        <source id="positions">
          <float_array id="positions-array" count="12">
            {-half} {-half} 0
            {half} {-half} 0
            {half} {half} 0
            {-half} {half} 0
          </float_array>
          <technique_common>
            <accessor source="#positions-array" count="4" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <source id="normals">
          <float_array id="normals-array" count="3">0 0 1</float_array>
          <technique_common>
            <accessor source="#normals-array" count="1" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <source id="uvs">
          <float_array id="uvs-array" count="8">0 0 1 0 1 1 0 1</float_array>
          <technique_common>
            <accessor source="#uvs-array" count="4" stride="2">
              <param name="S" type="float"/>
              <param name="T" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <vertices id="vertices">
          <input semantic="POSITION" source="#positions"/>
        </vertices>
        <triangles material="aruco_material" count="2">
          <input semantic="VERTEX" source="#vertices" offset="0"/>
          <input semantic="NORMAL" source="#normals" offset="1"/>
          <input semantic="TEXCOORD" source="#uvs" offset="2" set="0"/>
          <p>0 0 0 1 0 1 2 0 2 0 0 0 2 0 2 3 0 3</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="ArUco" name="ArUco" type="NODE">
        <instance_geometry url="#aruco_plane">
          <bind_material>
            <technique_common>
              <instance_material symbol="aruco_material" target="#aruco_material">
                <bind_vertex_input semantic="UVMap" input_semantic="TEXCOORD" input_set="0"/>
              </instance_material>
            </technique_common>
          </bind_material>
        </instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene>
    <instance_visual_scene url="#Scene"/>
  </scene>
</COLLADA>'''
    
    os.makedirs(output_dir, exist_ok=True)
    dae_path = os.path.join(output_dir, dae_filename)
    
    with open(dae_path, 'w') as f:
        f.write(dae_content)
    
    print(f"✓ Generado: {dae_path}")
    return dae_path


def main():
    parser = argparse.ArgumentParser(description="Genera assets ArUco para Gazebo")
    parser.add_argument("--output", "-o", 
                        default="../models/aruco_marker",
                        help="Directorio de salida")
    parser.add_argument("--id", "-i", type=int, default=23,
                        help="ID del marcador ArUco (default: 23)")
    parser.add_argument("--size", "-s", type=float, default=0.2,
                        help="Tamaño del marcador en metros (default: 0.2)")
    parser.add_argument("--pixels", "-p", type=int, default=200,
                        help="Resolución de la imagen PNG (default: 200)")
    
    args = parser.parse_args()
    
    # Resolver path relativo desde ubicación del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.normpath(os.path.join(script_dir, args.output))
    
    print(f"\n=== Generando ArUco ID {args.id} ({args.size}m) ===")
    print(f"Directorio: {output_dir}\n")
    
    # Generar PNG
    png_path = generate_aruco_png(output_dir, args.id, args.pixels)
    if not png_path:
        print("\n⚠ No se pudo generar PNG. Crea manualmente aruco_23.png")
    
    # Generar DAE
    generate_aruco_dae(output_dir, args.id, args.size)
    
    print(f"\n✅ Assets generados en: {output_dir}")
    print("   Ahora ejecuta: colcon build --packages-select go2_config")


if __name__ == "__main__":
    main()
