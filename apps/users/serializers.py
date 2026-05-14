from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'min_length': 'Пароль должен содержать минимум 8 символов.',
            'blank': 'Пароль не может быть пустым.',
        }
    )

    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'patronymic',
            'password',
            'password_confirm',
        ]

        extra_kwargs = {
            'email': {
                'error_messages': {
                    'unique': 'Пользователь с таким email уже существует.',
                    'blank': 'Email не может быть пустым.',
                }
            },
            'first_name': {
                'error_messages': {'blank': 'Имя не может быть пустым.'}
            },
            'last_name': {
                'error_messages': {'blank': 'Фамилия не может быть пустой.'}
            },
        }

    def validate_email(self, value):
        return value.lower().strip()
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
                raise serializers.ValidationError({
                    'password_confirm': 'Пароли не совпадают.'
        })
        return data
    
    def create(self, validated_data):
         validated_data.pop('password_confirm')
         user = User.objects.create_user(**validated_data)
         return user
    
class UserProfileSerializer(serializers.ModelSerializer):
     class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'patronymic',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
             'id',
             'email',
             'is_active',
             'created_at',
             'updated_at',
        ]

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
          model = User
          fields = [
               'first_name',
               'last_name',
               'patronymic',
          ]

          extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'patronymic': {'required': False},
          }

    def validate_first_name(self, value):
        if value is not None and value.strip() == '':
              raise serializers.ValidationError('Имя не может быть пустым.')
        return value.strip() if value else value

    def validate_last_name(self, value):
        if value is not None and value.strip() == '':
              raise serializers.ValidationError('Фамилия не может быть пустой.')
        return value.strip() if value else value
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.patronymic = validated_data.get('patronymic', instance.patronymic)
        instance.save()  
        return instance
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Новые пароли не совпадают.'
            })
        return data