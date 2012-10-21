from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object
from rupypy.utils.ordereddict import OrderedDict


class W_HashObject(W_Object):
    classdef = ClassDef("Hash", W_Object.classdef)

    def __init__(self, space):
        W_Object.__init__(self, space)
        self.contents = OrderedDict(space.eq_w, space.hash_w)
        self.w_default = space.w_nil

    @classdef.singleton_method("allocate")
    def method_allocate(self, space):
        return W_HashObject(space)

    @classdef.singleton_method("[]")
    def singleton_method_subscript(self, space, w_obj):
        w_res = space.convert_type(w_obj, space.w_hash, "to_hash")
        if w_res is space.w_nil:
            raise NotImplementedError
        assert isinstance(w_res, W_HashObject)
        result = W_HashObject(space)
        result.contents.update(w_res.contents)
        return result

    @classdef.method("initialize")
    def method_initialize(self, space, w_default=None):
        if w_default is not None:
            self.w_default = w_default

    @classdef.method("[]")
    def method_subscript(self, space, w_key):
        return self.contents.get(w_key, self.w_default)

    @classdef.method("[]=")
    def method_subscript_assign(self, w_key, w_value):
        self.contents[w_key] = w_value
        return w_value

    @classdef.method("size")
    def method_size(self, space):
        return space.newint(len(self.contents))

    @classdef.method("delete")
    def method_delete(self, space, w_key):
        return self.contents.pop(w_key, space.w_nil)

    @classdef.method("keys")
    def method_keys(self, space):
        return space.newarray(self.contents.keys())

    @classdef.method("values")
    def method_values(self, space):
        return space.newarray(self.contents.values())

    @classdef.method("to_hash")
    def method_to_hash(self, space):
        return self

    classdef.app_method("""
    def each
        iter = Topaz::HashIterator.new(self)
        while true
            begin
                key, value = iter.next()
            rescue StopIteration
                return
            end
            yield key, value
        end
    end
    alias each_pair each
    """)

    @classdef.method("key?")
    @classdef.method("has_key?")
    @classdef.method("member?")
    @classdef.method("include?")
    def method_includep(self, space, w_key):
        return space.newbool(w_key in self.contents)

    classdef.app_method("""
    def ==(other)
        if self.equal?(other)
            return true
        end
        if !other.kind_of?(Hash)
            return false
        end
        if self.size != other.size
            return false
        end
        self.each do |key, value|
            if !other.has_key?(key) || other[key] != value
                return false
            end
        end
        return true
    end
    """)


class W_HashIterator(W_Object):
    classdef = ClassDef("HashIterator", W_Object.classdef)

    def __init__(self, space, d):
        W_Object.__init__(self, space)
        self.iterator = d.iteritems()

    @classdef.singleton_method("allocate")
    def method_allocate(self, space, w_obj):
        assert isinstance(w_obj, W_HashObject)
        return W_HashIterator(space, w_obj.contents)

    @classdef.method("next")
    def method_next(self, space):
        try:
            w_k, w_v = self.iterator.next()
        except StopIteration:
            raise space.error(space.w_StopIteration)
        return space.newarray([w_k, w_v])
