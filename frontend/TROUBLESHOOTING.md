# Troubleshooting - Shafan Frontend

## Error: Cannot find module './586.js' or similar

### Síntomas

```
⨯ Error: Cannot find module './586.js'
⨯ Error: Cannot find module './611.js'
[TypeError: Cannot read properties of undefined (reading '/_app')]
```

### Causa

Este error ocurre cuando el cache de Next.js se corrompe, típicamente después de:

- Cambios estructurales en carpetas
- Eliminación de archivos/carpetas
- Actualización de dependencias
- Interrupciones durante el build

### Solución

#### Opción 1: Script de limpieza completa (RECOMENDADO)

```bash
cd frontend
rm -rf .next
rm -rf node_modules/.cache
npm run dev
```

#### Opción 2: Limpieza con npm clean

```bash
cd frontend
npm run clean  # Si tienes este script configurado
npm run dev
```

#### Opción 3: Reinstalación completa (si el problema persiste)

```bash
cd frontend
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```

---

## Errores comunes después de cambios estructurales

### 1. Module not found en desarrollo

**Solución:** Reinicia el dev server con cache limpio

```bash
rm -rf .next && npm run dev
```

### 2. TypeScript errors no se reflejan

**Solución:** Limpia y verifica tipos

```bash
rm -rf .next
npm run type-check
npm run dev
```

### 3. Cambios en archivos no se reflejan

**Solución:** Hard reload del navegador

- Chrome/Edge: `Ctrl+Shift+R` (Windows/Linux) o `Cmd+Shift+R` (Mac)
- Firefox: `Ctrl+F5` (Windows/Linux) o `Cmd+Shift+R` (Mac)

---

## Build errors en producción

### Error durante npm run build

```bash
# Limpia completamente
rm -rf .next
rm -rf node_modules/.cache

# Rebuild
npm run build
```

### Error: ENOSPC (System limit for file watchers)

**En Linux:**

```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Errores de ESLint

### "Module type not specified" warning

Agregar en `package.json`:

```json
{
  "type": "module"
}
```

**NOTA:** No hagas esto todavía ya que puede romper otros scripts.

---

## Verificación después de limpieza

Después de limpiar el cache, verifica que todo funcione:

```bash
# 1. Type check
npm run type-check

# 2. Lint
npm run lint

# 3. Build
npm run build

# 4. Start dev
npm run dev
```

---

## Prevención

Para evitar problemas de cache:

1. **Detén el dev server** antes de hacer cambios estructurales grandes
2. **Limpia el cache** después de cambios importantes:
   ```bash
   rm -rf .next
   ```
3. **Usa Fast Refresh** - Next.js detecta cambios automáticamente
4. **Evita modificar** archivos en `.next/` manualmente

---

## Contacto

Si ninguna de estas soluciones funciona:

1. Revisa los logs completos en la terminal
2. Busca errores específicos en GitHub Issues de Next.js
3. Contacta al equipo del proyecto
