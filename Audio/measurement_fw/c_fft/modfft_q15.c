/* MicroPython module: fft_q15
 *
 *   import fft_q15
 *   from array import array
 *   f = fft_q15.FFT(1024)
 *   out = array('i', bytearray(4 * (1024//2 + 1)))
 *   f.power_into(samples, out)
 *   denom = f.full_scale_power(1 << 23)
 *   sh = f.shift()
 */
#include "py/obj.h"
#include "py/runtime.h"

#include "fft_q15.h"

typedef struct _mp_fft_q15_obj_t {
    mp_obj_base_t base;
    fft_q15_t fft;
} mp_fft_q15_obj_t;

static mp_obj_t mp_fft_q15_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 1, 1, false);
    int n = mp_obj_get_int(args[0]);
    size_t words = fft_q15_store_words(n);
    if (words == 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("n must be power of 2 (>=4)"));
    }
    mp_fft_q15_obj_t *self = mp_obj_malloc(mp_fft_q15_obj_t, type);
    /* The GC heap owns nearly all RAM here, so libc calloc would return memory
     * overlapping it and lock the chip on the first table write. */
    int32_t *store = m_new(int32_t, words);
    if (fft_q15_init_with(&self->fft, n, store) != 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("n must be power of 2 (>=4)"));
    }
    return MP_OBJ_FROM_PTR(self);
}

static int is_i32_buf(const mp_buffer_info_t *info, size_t need_bytes) {
    if (info->len < need_bytes) {
        return 0;
    }
    /* array.array('i') / ('l' on some ports) */
    return info->typecode == 'i' || info->typecode == 'l';
}

static mp_obj_t mp_fft_q15_power_into(mp_obj_t self_in, mp_obj_t samples_in, mp_obj_t out_in) {
    mp_fft_q15_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t srcinfo, dstinfo;
    mp_get_buffer_raise(samples_in, &srcinfo, MP_BUFFER_READ);
    mp_get_buffer_raise(out_in, &dstinfo, MP_BUFFER_WRITE);
    int n = self->fft.n;
    int half1 = (n >> 1) + 1;
    if (!is_i32_buf(&srcinfo, (size_t)n * 4)) {
        mp_raise_ValueError(MP_ERROR_TEXT("samples need n int32"));
    }
    if (!is_i32_buf(&dstinfo, (size_t)half1 * 4)) {
        mp_raise_ValueError(MP_ERROR_TEXT("out need n/2+1 int32"));
    }
    fft_q15_power_into(&self->fft, srcinfo.buf, dstinfo.buf);
    return out_in;
}
static MP_DEFINE_CONST_FUN_OBJ_3(mp_fft_q15_power_into_obj, mp_fft_q15_power_into);

static mp_obj_t mp_fft_q15_full_scale_power(mp_obj_t self_in, mp_obj_t ref_in) {
    mp_fft_q15_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_float(fft_q15_full_scale_power(&self->fft, mp_obj_get_float(ref_in)));
}
static MP_DEFINE_CONST_FUN_OBJ_2(mp_fft_q15_full_scale_power_obj, mp_fft_q15_full_scale_power);

static mp_obj_t mp_fft_q15_shift(mp_obj_t self_in) {
    mp_fft_q15_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return MP_OBJ_NEW_SMALL_INT(self->fft.shift);
}
static MP_DEFINE_CONST_FUN_OBJ_1(mp_fft_q15_shift_obj, mp_fft_q15_shift);

static mp_obj_t mp_fft_q15_n(mp_obj_t self_in) {
    mp_fft_q15_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return MP_OBJ_NEW_SMALL_INT(self->fft.n);
}
static MP_DEFINE_CONST_FUN_OBJ_1(mp_fft_q15_n_obj, mp_fft_q15_n);

static const mp_rom_map_elem_t mp_fft_q15_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_power_into), MP_ROM_PTR(&mp_fft_q15_power_into_obj) },
    { MP_ROM_QSTR(MP_QSTR_full_scale_power), MP_ROM_PTR(&mp_fft_q15_full_scale_power_obj) },
    { MP_ROM_QSTR(MP_QSTR_shift), MP_ROM_PTR(&mp_fft_q15_shift_obj) },
    { MP_ROM_QSTR(MP_QSTR_n), MP_ROM_PTR(&mp_fft_q15_n_obj) },
};
static MP_DEFINE_CONST_DICT(mp_fft_q15_locals_dict, mp_fft_q15_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    mp_fft_q15_type,
    MP_QSTR_FFT,
    MP_TYPE_FLAG_NONE,
    make_new, mp_fft_q15_make_new,
    locals_dict, &mp_fft_q15_locals_dict
);

static const mp_rom_map_elem_t fft_q15_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_fft_q15) },
    { MP_ROM_QSTR(MP_QSTR_FFT), MP_ROM_PTR(&mp_fft_q15_type) },
};
static MP_DEFINE_CONST_DICT(fft_q15_module_globals, fft_q15_module_globals_table);

const mp_obj_module_t fft_q15_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&fft_q15_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_fft_q15, fft_q15_user_cmodule);
